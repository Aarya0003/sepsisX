import api from "./api";
import { Alert, AlertStatus } from "@/types";

export const getAlerts = async (
  status?: AlertStatus,
  skip = 0,
  limit = 100
): Promise<Alert[]> => {
  const statusParam = status ? `status=${status}&` : "";
  const response = await api.get<Alert[]>(
    `/api/v1/alerts?${statusParam}skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const getPendingAlerts = async (
  skip = 0,
  limit = 100
): Promise<Alert[]> => {
  const response = await api.get<Alert[]>(
    `/api/v1/alerts/pending?skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const getPatientAlerts = async (
  patientId: string,
  skip = 0,
  limit = 100
): Promise<Alert[]> => {
  const response = await api.get<Alert[]>(
    `/api/v1/alerts/patient/${patientId}?skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const getAlert = async (alertId: string): Promise<Alert> => {
  const response = await api.get<Alert>(`/api/v1/alerts/${alertId}`);
  return response.data;
};

export const updateAlertStatus = async (
  alertId: string,
  status: AlertStatus
): Promise<Alert> => {
  const response = await api.put<Alert>(`/api/v1/alerts/${alertId}/status`, {
    status,
  });
  return response.data;
};

export const sendAlertNotification = async (alertId: string): Promise<any> => {
  const response = await api.post(
    `/api/v1/alerts/${alertId}/send-notification`
  );
  return response.data;
};
