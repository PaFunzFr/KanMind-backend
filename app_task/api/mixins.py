class CommentCountMixin:
    def get_comments_count(self, obj):
        return obj.comments.count()