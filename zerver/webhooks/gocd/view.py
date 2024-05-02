import json
import os

from django.http import HttpRequest, HttpResponse

from zerver.decorator import webhook_view
from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import JsonBodyPayload, typed_endpoint
from zerver.lib.validator import WildValue,check_string
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile

@webhook_view("GoCD")
@typed_endpoint
def api_gocd_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    *,
    payload: JsonBodyPayload[dict],
) -> HttpResponse:
    build_cause = payload["build_cause"]
    stages = payload["stages"]

    author = build_cause["material_revisions"][0]["modifications"][0]["user_name"]
    comment = build_cause["material_revisions"][0]["modifications"][0]["comment"]

    pipeline_name = payload["name"]
    build_status = "Passed" if all(stage["result"] == "Passed" for stage in stages) else "Failed"
    emoji = ":thumbs_up:" if build_status == "Passed" else ":thumbs_down:"

    build_details_file = os.path.join(os.path.dirname(__file__), "fixtures/build_details.json")

    with open(build_details_file) as f:
        build_details = json.load(f)
        build_link = build_details["build_details"]["_links"]["pipeline"]["href"]

    body = f"Author: {author}\nBuild status: {build_status} {emoji}\nDetails: [build log]({build_link})\nComment: {comment}"
    topic_name = pipeline_name

    check_send_webhook_message(request, user_profile, topic_name, body)




    return json_success(request)
