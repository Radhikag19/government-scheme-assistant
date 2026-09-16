import uuid


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(self, scheme_id=None):
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "scheme_id": scheme_id,
            "history": []
        }

        return session_id

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def set_scheme(self, session_id, scheme_id):

        session = self.sessions.get(session_id)

        if session is None:
            return False

        session["scheme_id"] = scheme_id

        return True

    def add_message(
        self,
        session_id,
        role,
        content
    ):

        session = self.sessions.get(session_id)

        if session is None:
            return False

        session["history"].append({
            "role": role,
            "content": content
        })

        return True

    def get_history(self, session_id):

        session = self.sessions.get(session_id)

        if session is None:
            return []

        return session["history"]

    def clear_session(self, session_id):

        if session_id in self.sessions:

            self.sessions[session_id] = {
                "scheme_id": None,
                "history": []
            }

            return True

        return False
