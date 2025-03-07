import React from "react";
import {
  VStack,
  Box,
  Flex,
  Text,
  Icon,
  Heading,
  Divider,
} from "@chakra-ui/react";
import { useRouter } from "next/router";
import Link from "next/link";
import {
  FiHome,
  FiUsers,
  FiAlertCircle,
  FiBarChart2,
  FiSettings,
  FiLogOut,
} from "react-icons/fi";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  onItemClick?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onItemClick }) => {
  const router = useRouter();
  const { user, logout } = useAuth();

  const isActive = (path: string) => router.pathname === path;

  const menuItems = [
    {
      name: "Dashboard",
      icon: FiHome,
      path: "/dashboard",
      roles: ["admin", "doctor", "nurse"],
    },
    {
      name: "Patients",
      icon: FiUsers,
      path: "/patients",
      roles: ["admin", "doctor", "nurse"],
    },
    {
      name: "Alerts",
      icon: FiAlertCircle,
      path: "/alerts",
      roles: ["admin", "doctor", "nurse"],
    },
    {
      name: "Analytics",
      icon: FiBarChart2,
      path: "/analytics",
      roles: ["admin", "doctor"],
    },
    { name: "Settings", icon: FiSettings, path: "/settings", roles: ["admin"] },
  ];

  const filteredMenuItems = menuItems.filter(
    (item) => user && item.roles.includes(user.role)
  );

  return (
    <Box height="100%" py={5}>
      <Flex justify="center" mb={8}>
        <Heading size="md" color="white">
          Sepsis Prediction
        </Heading>
      </Flex>

      <VStack spacing={1} align="stretch">
        {filteredMenuItems.map((item) => (
          <Link href={item.path} key={item.path}>
            <Box
              onClick={onItemClick}
              px={5}
              py={3}
              cursor="pointer"
              bg={isActive(item.path) ? "blue.700" : "transparent"}
              _hover={{ bg: "blue.700" }}
              borderLeftWidth={isActive(item.path) ? "4px" : "0"}
              borderLeftColor="blue.400"
            >
              <Flex align="center">
                <Icon as={item.icon} mr={3} />
                <Text>{item.name}</Text>
              </Flex>
            </Box>
          </Link>
        ))}
      </VStack>

      <Divider my={6} borderColor="whiteAlpha.400" />

      <Box
        px={5}
        py={3}
        cursor="pointer"
        onClick={logout}
        _hover={{ bg: "blue.700" }}
      >
        <Flex align="center">
          <Icon as={FiLogOut} mr={3} />
          <Text>Logout</Text>
        </Flex>
      </Box>
    </Box>
  );
};

export default Sidebar;
