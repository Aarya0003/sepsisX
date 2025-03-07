import React from "react";
import {
  Box,
  Flex,
  VStack,
  Heading,
  IconButton,
  useDisclosure,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
} from "@chakra-ui/react";
import { HamburgerIcon } from "@chakra-ui/icons";
import { useRouter } from "next/router";
import Sidebar from "@/components/layouts/Sidebar";
import NavBar from "@/components/layouts/NavBar";
import { useAuth } from "@/contexts/AuthContext";

interface MainLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children, title }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!loading && !isAuthenticated && router.pathname !== "/login") {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  if (loading) {
    return (
      <Flex justifyContent="center" alignItems="center" height="100vh">
        <Heading>Loading...</Heading>
      </Flex>
    );
  }

  if (!isAuthenticated && router.pathname !== "/login") {
    return null; // Will redirect in the effect
  }

  return (
    <Flex minHeight="100vh" direction={{ base: "column", md: "row" }}>
      {/* Sidebar - visible on desktop, hidden on mobile */}
      <Box
        display={{ base: "none", md: "block" }}
        width="250px"
        bg="blue.800"
        color="white"
      >
        <Sidebar />
      </Box>

      {/* Mobile sidebar drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody p={0}>
            <Sidebar onItemClick={onClose} />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main content */}
      <Box flex="1" bg="gray.50">
        {/* Top navigation bar */}
        <NavBar
          title={title}
          onMenuClick={onOpen}
          userName={user?.full_name || ""}
        />

        {/* Page content */}
        <Box p={4} maxWidth="1600px" mx="auto">
          {children}
        </Box>
      </Box>
    </Flex>
  );
};

export default MainLayout;
