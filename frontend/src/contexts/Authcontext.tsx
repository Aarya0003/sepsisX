import React, { createContext, useState, useEffect, useContext } from "react";
import { useRouter } from "next/router";
import { User, AuthToken } from "@/types";
import { login as apiLogin, getCurrentUser } from "@/services/auth.service";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load user on initial load
  useEffect(() => {
    const loadUser = async () => {
      try {
        // Check if token exists
        const token = localStorage.getItem("token");
        if (!token) {
          setLoading(false);
          return;
        }

        // Fetch current user
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        // Clear invalid tokens
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      const authData = await apiLogin(email, password);

      // Save token and user in localStorage
      localStorage.setItem("token", authData.access_token);

      // Set the user state
      const userData: User = {
        id: authData.user_id,
        email: authData.email,
        full_name: authData.full_name,
        role: authData.role,
        is_active: true,
      };

      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);

      // Redirect to dashboard
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    // Reset state
    setUser(null);

    // Redirect to login
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
