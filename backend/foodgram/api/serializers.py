from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow
from users.serializers import CustomUserSerializers


class FollowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return FollowRecipeSerializers(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    class Meta:
        model = Follow
        fields = '__all__'


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = '__all__'


class RecipeSerializers(serializers.ModelSerializer):
    tags = TagSerializers(read_only=True, many=True)
    author = CustomUserSerializers(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializers(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()


class RecipeWriteSerializers(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = CustomUserSerializers(read_only=True)
    ingredients = IngredientRecipeSerializers(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, data):
        ingredients = data
        if not ingredients:
            raise ValidationError('Добавьте ингредиент в рецепт')
        valid_ingredients = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in valid_ingredients:
                raise ValidationError(
                    'Ингредиент может быть добавлен только один раз')
            if int(item['amount']) <= 0:
                raise ValidationError(
                    'Добавьте количество для ингредиента больше 0')
            valid_ingredients.append(ingredient)
        return data

    def ingredient_recipe_create(self, ingredients_set, recipe):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=get_object_or_404(Ingredient,
                                             id=ingredient_get['id']),
                recipe=recipe,
                amount=ingredient_get['amount']
            ) for ingredient_get in ingredients_set]
        )

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients_set = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image,
                                       author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.ingredient_recipe_create(ingredients_set, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients_set = self.validated_data.pop('ingredients')
        self.ingredient_recipe_create(ingredients_set, instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializers(instance, context=context).data


class FavoriteSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCardSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = '__all__'
