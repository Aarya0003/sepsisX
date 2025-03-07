import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import { Box, Spinner, Center, Text } from "@chakra-ui/react";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        router.push("/dashboard");
      } else {
        router.push("/login");
      }
    }
  }, [isAuthenticated, loading, router]);

  return (
    <Center h="100vh">
      <Box textAlign="center">
        <Spinner size="xl" mb={4} color="blue.500" />
        <Text fontSize="xl">Loading Sepsis Prediction System...</Text>
      </Box>
    </Center>
  );
}
