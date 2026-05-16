from rest_framework import serializers
from .models import Category, Tag, Event, Registration, Review, EventMedia


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ('id', 'file', 'uploaded_at')


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source='tags', write_only=True, required=False
    )
    registration_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'category', 'category_detail',
            'tags', 'tag_ids', 'status', 'event_type', 'start_date', 'end_date',
            'location', 'max_attendees', 'created_at', 'registration_count', 'avg_rating',
        )
        read_only_fields = ('organizer', 'created_at')

    def get_registration_count(self, obj):
        return obj.registrations.filter(status='confirmed').count()

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        result = obj.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        event = Event.objects.create(**validated_data)
        event.tags.set(tags)
        return event

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Registration
        fields = ('id', 'user', 'event', 'status', 'registered_at')
        read_only_fields = ('user', 'event', 'registered_at')

    def validate(self, data):
        request = self.context['request']
        event = self.context['event']

                         
        if Registration.objects.filter(user=request.user, event=event).exists():
            raise serializers.ValidationError("You are already registered for this event.")

                        
        if event.is_full:
            raise serializers.ValidationError("This event is full.")

        return data

    def create(self, validated_data):
        request = self.context['request']
        event = self.context['event']
        return Registration.objects.create(
            user=request.user, event=event, status='confirmed', **validated_data
        )


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'user', 'event', 'rating', 'comment', 'created_at')
        read_only_fields = ('user', 'event', 'created_at')

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        request = self.context['request']
        event = self.context['event']
        if Review.objects.filter(user=request.user, event=event).exists():
            raise serializers.ValidationError("You have already reviewed this event.")
        return data

    def create(self, validated_data):
        request = self.context['request']
        event = self.context['event']
        return Review.objects.create(user=request.user, event=event, **validated_data)