import markdown

from ..api.models import AnswerResponse, EmbedQuestionResponse, ResourceResponse


def answer_response_to_html(answer_response: AnswerResponse):
    answer = answer_response.answer
    answer += "\n\n## Related Videos\n\n"
    for i, resource in enumerate(answer_response.resources):
        answer += f'\n{i+1}. {resource.segment_title}\n <iframe width="770" height="400" src="{resource.url.replace("watch?v=", "embed/").replace("&t=", "?start=")[:-1]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n'

    html = markdown.markdown(answer, extensions=['extra'])
    return html


def resource_response_to_html(resource_response: ResourceResponse):
    output = "\n\n## Related Videos\n\n"
    for i, resource in enumerate(resource_response.resources):
        output += f'\n{i+1}. {resource.segment_title}\n <iframe width="770" height="400" src="{resource.url.replace("watch?v=", "embed/").replace("&t=", "?start=")[:-1]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n'

    html = markdown.markdown(output, extensions=['extra'])
    return html
