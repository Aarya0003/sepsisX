import React from "react";
import {
  Flex,
  Box,
  Heading,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  Text,
  Badge,
} from "@chakra-ui/react";
import { HamburgerIcon, BellIcon } from "@chakra-ui/icons";
import { useRouter } from "next/router";

interface NavBarProps {
  title?: string;
  onMenuClick: () => void;
  userName: string;
}

const NavBar: React.FC<NavBarProps> = ({ title, onMenuClick, userName }) => {
  const router = useRouter();

  return (
    <Flex
      as="nav"
      align="center"
      justify="space-between"
      wrap="wrap"
      padding="1rem"
      bg="white"
      boxShadow="sm"
    >
      {/* Left side - Mobile menu and title */}
      <Flex align="center">
        <IconButton
          display={{ base: "flex", md: "none" }}
          aria-label="Menu"
          icon={<HamburgerIcon />}
          onClick={onMenuClick}
          variant="ghost"
          mr={2}
        />
        <Heading size="md">{title || "Sepsis Prediction System"}</Heading>
      </Flex>

      {/* Right side - Notifications and user menu */}
      <Flex align="center">
        {/* Notifications */}
        <Box position="relative" mr={4}>
          <IconButton
            aria-label="Notifications"
            icon={<BellIcon />}
            variant="ghost"
            onClick={() => router.push("/alerts")}
          />
          <Badge
            position="absolute"
            top="-2px"
            right="-2px"
            colorScheme="red"
            borderRadius="full"
          >
            5
          </Badge>
        </Box>

        {/* User menu */}
        <Menu>
          <MenuButton>
            <Flex align="center">
              <Avatar size="sm" mr={2} name={userName} />
              <Text display={{ base: "none", md: "block" }}>{userName}</Text>
            </Flex>
          </MenuButton>
          <MenuList>
            <MenuItem onClick={() => router.push("/profile")}>Profile</MenuItem>
            <MenuItem onClick={() => router.push("/settings")}>
              Settings
            </MenuItem>
            <MenuItem onClick={() => router.push("/logout")}>Logout</MenuItem>
          </MenuList>
        </Menu>
      </Flex>
    </Flex>
  );
};

export default NavBar;
