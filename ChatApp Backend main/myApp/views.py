from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserLoginSerializer, OutfitGeneratorInputSerializer
import openai
from elasticsearch import Elasticsearch
from collections import defaultdict
from .models import CustomUser, Brand, ClothingItem, Interest, Conversation, Tag

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OutfitGeneratorView(APIView):
    permission_classes = [IsAuthenticated]

    conversation_states = defaultdict(dict)

    def post(self, request):
        serializer = OutfitGeneratorInputSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id
            user_prompt = serializer.validated_data['prompt']
            user_age = serializer.validated_data['age']
            user_location = serializer.validated_data['location']

            conversation = self.conversation_states[user_id]

            if 'history' not in conversation:
                conversation['history'] = []

            conversation['history'].append(user_prompt)

            combined_prompt = "\n".join(conversation['history'])
            openai_terms = generate_openai_terms(combined_prompt, user_age, user_location)
            recommendations = generate_outfit_recommendations(openai_terms, user_id)

            return Response({"outfit_recommendations": recommendations}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_openai_terms(prompt, age, location):
    openai.api_key = "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"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )

    return response.choices[0].text.strip()

def generate_outfit_recommendations(search_terms, user_id):
    es_client = Elasticsearch([{'host': 'your-elasticsearch-host', 'port': 9200}])

    es_query = {
        "query": {
            "match": {
                "clothing_item": search_terms
            }
        }
    }

    results = es_client.search(index='clothing_catalog', body=es_query)
    recommendations = process_es_results(results)

    # Enhance recommendations based on user preferences and interests
    user = CustomUser.objects.get(pk=user_id)
    favorite_brands = user.favorite_brands.all()
    interests = user.interests.all()

    enhanced_recommendations = []
    for item in recommendations:
        if item.brand in favorite_brands or any(interest.name in item.description for interest in interests):
            enhanced_recommendations.append(item)

    return enhanced_recommendations

def process_es_results(es_results):
    recommendations = []
    for hit in es_results['hits']['hits']:
        clothing_item_id = hit['_source']['id']
        clothing_item = ClothingItem.objects.get(pk=clothing_item_id)
        recommendations.append(clothing_item)
    return recommendations
