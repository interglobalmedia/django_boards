from django import forms
from .models import Topic, Post
import nh3

class HtmlSanitizedCharField(forms.CharField):
    def to_python(self, value):
        value = super().to_python(value)
        print(value, 'the Charfield value')
        if value not in self.empty_values:
            value = nh3.clean(
                value,
                # Allow only tags and attributes from our rich text editor
                tags={
                    "a",
                    "abbr",
                    "acronym",
                    "b",
                    "blockquote",
                    "code",
                    "em",
                    "i",
                    "li",
                    "ol",
                    "strong",
                    "ul",
                    "s",
                    "sup",
                    "sub",
                },
                attributes={
                    "a": {"href"},
                    "abbr": {"title"},
                    "acronym": {"title"},
                },
                url_schemes={"https"},
                link_rel=None,)
        return value

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "What is on your mind?"}
        ),
    )

    class Meta:
        model = Topic
        fields = ["subject", "message"]

class PostForm(forms.ModelForm):
    message = HtmlSanitizedCharField(widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ['message']