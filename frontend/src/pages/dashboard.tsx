import React, { useEffect, useState } from 'react';
import { Box, Grid, Heading, Text, Stat, StatLabel, StatNumber, StatHelpText, Flex, Button, useColorModeValue, SimpleGrid } from
import React, { useEffect, useState } from 'react';
import { Box, Grid, Heading, Text, Stat, StatLabel, StatNumber, StatHelpText, Flex, Button, useColorModeValue, SimpleGrid } from '@chakra-ui/react';
import MainLayout from '@/components/layouts/MainLayout';
import { useAuth } from '@/contexts/AuthContext';
import { getPendingAlerts } from '@/services/alert.service';
import { getPatients } from '@/services/patient.service';
import { Alert, Patient } from '@/types';
import AlertCard from '@/components/alerts/AlertCard';
import PatientListItem from '@/components/patients/PatientListItem';
import { Chart } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();
  
  const bgCard = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [alertsData, patientsData] = await Promise.all([
          getPendingAlerts(0, 5),
          getPatients(0, 5)
        ]);
        
        setAlerts(alertsData);
        setPatients(patientsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data for sepsis predictions
  const predictionChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Sepsis Cases',
        data: [12, 19, 10, 15, 8, 13],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Early Detections',
        data: [7, 11, 5, 8, 3, 9],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Sepsis Cases Over Time',
      },
    },
  };

  return (
    <MainLayout title="Dashboard">
      <Box mb={8}>
        <Heading size="lg" mb={2}>Welcome, {user?.full_name}</Heading>
        <Text color="gray.600">Here's an overview of the sepsis monitoring system</Text>
      </Box>

      {/* Stats Section */}
      <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6} mb={8}>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
          <Stat>
            <StatLabel>Active Patients</StatLabel>
            <StatNumber>42</StatNumber>
            <StatHelpText>Currently monitored</StatHelpText>
          </Stat>
        </Box>
        
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
          <Stat>
            <StatLabel>Pending Alerts</StatLabel>
            <StatNumber>{alerts.length}</StatNumber>
            <StatHelpText>Require attention</StatHelpText>
          </Stat>
        </Box>
        
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
          <Stat>
            <StatLabel>High Risk Patients</StatLabel>
            <StatNumber>8</StatNumber>
            <StatHelpText>Probability > 60%</StatHelpText>
          </Stat>
        </Box>
        
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
          <Stat>
            <StatLabel>Detected Early</StatLabel>
            <StatNumber>94%</StatNumber>
            <StatHelpText>Success rate</StatHelpText>
          </Stat>
        </Box>
      </SimpleGrid>

      {/* Main Content Grid */}
      <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={8}>
        {/* Left Column */}
        <Box>
          {/* Recent Alerts */}
          <Box mb={8} p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="md">Recent Alerts</Heading>
              <Button size="sm" colorScheme="blue" onClick={() => window.location.href = '/alerts'}>
                View All
              </Button>
            </Flex>
            
            {isLoading ? (
              <Text>Loading alerts...</Text>
            ) : alerts.length > 0 ? (
              alerts.map(alert => (
                <AlertCard key={alert.id} alert={alert} />
              ))
            ) : (
              <Text>No pending alerts</Text>
            )}
          </Box>
          
          {/* Recent Patients */}
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="md">Recent Patients</Heading>
              <Button size="sm" colorScheme="blue" onClick={() => window.location.href = '/patients'}>
                View All
              </Button>
            </Flex>
            
            {isLoading ? (
              <Text>Loading patients...</Text>
            ) : patients.length > 0 ? (
              patients.map(patient => (
                <PatientListItem key={patient.id} patient={patient} />
              ))
            ) : (
              <Text>No patients found</Text>
            )}
          </Box>
        </Box>
        
        {/* Right Column */}
        <Box>
          {/* Sepsis Prediction Chart */}
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard} mb={8}>
            <Heading size="md" mb={4}>Sepsis Trends</Heading>
            <Box height="300px">
              <Chart type='line' data={predictionChartData} options={chartOptions} />
            </Box>
          </Box>
          
          {/* Quick Actions */}
          <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={bgCard}>
            <Heading size="md" mb={4}>Quick Actions</Heading>
            <SimpleGrid columns={2} spacing={4}>
              <Button colorScheme="blue" onClick={() => window.location.href = '/patients/new'}>
                Add Patient
              </Button>
              <Button colorScheme="green" onClick={() => window.location.href = '/predictions/batch'}>
                Batch Predict
              </Button>
              <Button colorScheme="purple" onClick={() => window.location.href = '/analytics'}>
                View Analytics
              </Button>
              <Button colorScheme="orange" onClick={() => window.location.href = '/settings'}>
                System Settings
              </Button>
            </SimpleGrid>
          </Box>
        </Box>
      </Grid>
    </MainLayout>
  );
};

export default Dashboard;