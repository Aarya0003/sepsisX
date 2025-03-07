import React, { useState } from "react";
import {
  Box,
  Flex,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Button,
  Text,
  useToast,
  Image,
  Link,
} from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const toast = useToast();
  const router = useRouter();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast({
        title: "Error",
        description: "Email and password are required",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setIsLoading(true);
      await login(email, password);
    } catch (error) {
      toast({
        title: "Login Failed",
        description: "Invalid email or password",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Flex
      minHeight="100vh"
      width="full"
      align="center"
      justifyContent="center"
      bg="gray.50"
    >
      <Box
        p={8}
        maxWidth="500px"
        borderWidth={1}
        borderRadius={8}
        boxShadow="lg"
        bg="white"
        width="90%"
      >
        <Box textAlign="center" mb={8}>
          <Heading size="xl" color="blue.600">
            Sepsis Prediction System
          </Heading>
          <Text mt={2} color="gray.600">
            Enter your credentials to access the system
          </Text>
        </Box>

        <Box my={4} textAlign="left">
          <form onSubmit={handleSubmit}>
            <FormControl isRequired mb={4}>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                placeholder="doctor@hospital.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </FormControl>

            <FormControl isRequired mb={6}>
              <FormLabel>Password</FormLabel>
              <Input
                type="password"
                placeholder="********"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </FormControl>

            <Button
              colorScheme="blue"
              width="full"
              mt={4}
              type="submit"
              isLoading={isLoading}
            >
              Sign In
            </Button>
          </form>

          <Text mt={6} textAlign="center">
            <Link color="blue.500" href="/forgot-password">
              Forgot password?
            </Link>
          </Text>
        </Box>
      </Box>
    </Flex>
  );
};

export default Login;
