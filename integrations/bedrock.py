import boto3, json, os

class BedrockReasoner:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")

    def reason(self, system_prompt: str, user_prompt: str) -> str:
        # Support both Anthropic Claude and Amazon Nova message formats
        model_id = self.model_id
        if "nova" in model_id or "titan" in model_id:
            body = {
                "messages": [
                    {"role": "user", "content": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
                ],
                "inferenceConfig": {"max_new_tokens": 4096}
            }
        else:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            }
        response = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        result = json.loads(response["body"].read())
        # Extract text from either response format
        if "content" in result:
            return result["content"][0]["text"]
        if "output" in result:
            return result["output"]["message"]["content"][0]["text"]
        return str(result)
