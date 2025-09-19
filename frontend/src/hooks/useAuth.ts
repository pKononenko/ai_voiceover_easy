import { useCallback, useEffect, useState } from "react";

const TOKEN_KEY = "voiceover_token";
const EMAIL_KEY = "voiceover_email";

interface AuthState {
  token: string | null;
  email: string | null;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({ token: null, email: null });

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const email = localStorage.getItem(EMAIL_KEY);
    if (token) {
      setState({ token, email });
    }
  }, []);

  const setAuth = useCallback((token: string, email: string) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(EMAIL_KEY, email);
    setState({ token, email });
  }, []);

  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    setState({ token: null, email: null });
  }, []);

  return {
    token: state.token,
    email: state.email,
    setAuth,
    clearAuth,
    isAuthenticated: Boolean(state.token),
  };
}
