import uuid



def generate_slug(name: str) -> str:
	base = name.lower().replace(' ', '-')[:80]
	return f"{base}-{uuid.uuid4().hex[:6]}"