from app import ma


class BlacklistSchema(ma.Schema):
    class Meta:
        fields = ("email", "app_uuid", "blocked_reason", "created_at", "blocked")

blacklist_schema = BlacklistSchema()
blacklists_schema = BlacklistSchema(many=True)