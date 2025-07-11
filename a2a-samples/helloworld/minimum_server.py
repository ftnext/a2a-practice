# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "uvicorn",
# ]
# ///
"""Example:
curl http://0.0.0.0:9999/.well-known/agent.json | jq .

curl -v http://0.0.0.0:9999/ --json '{"id": 1, "jsonrpc": "2.0", "method": "message/send", "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": "Hi"}], "messageId": "abc"}}}'
"""
import json
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


app = FastAPI(title='Minimum Support for Hello World test client')


@app.get('/.well-known/agent.json')
async def public_agent_card():
    return {
        'capabilities': {'streaming': True},
        'defaultInputModes': ['text'],
        'defaultOutputModes': ['text'],
        'description': 'Parrot agent',
        'name': 'Parrot Agent',
        'protocolVersion': '0.2.5',
        'skills': [
            {
                'description': 'just returns received text',
                'examples': ['hi', 'hello world'],
                'id': 'parrot',
                'name': 'Parrot',
                'tags': ['parrot'],
            }
        ],
        'url': 'http://localhost:9999/',
        'version': '1.0.0',
    }


class A2ARequestPart(BaseModel):
    kind: str
    text: str


class A2ARequestMessage(BaseModel):
    role: str
    parts: list[A2ARequestPart]
    messageId: str


class A2ARequestParameters(BaseModel):
    message: A2ARequestMessage


class A2ARequestJsonBody(BaseModel):
    id: int | str
    jsonrpc: Literal['2.0']
    method: str
    params: A2ARequestParameters


@app.post('/', status_code=status.HTTP_200_OK)
async def run(json_body: A2ARequestJsonBody):
    if json_body.method not in {'message/send', 'message/stream'}:
        raise NotImplementedError

    response = {
        'id': json_body.id,
        'jsonrpc': '2.0',
        'result': {
            'kind': 'message',
            'messageId': uuid4().hex,
            'parts': [
                {
                    'kind': 'text',
                    'text': ' '.join(
                        part.text for part in json_body.params.message.parts
                    ),
                }
            ],
            'role': 'agent',
        },
    }

    match json_body.method:
        case 'message/send':
            return response
        case 'message/stream':

            def generator():
                yield f'data: {json.dumps(response)}\n\n'

            return StreamingResponse(
                content=generator(),
                media_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Cache-Control',
                },
            )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='localhost', port=9999)
