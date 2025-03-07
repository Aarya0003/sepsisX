import api from "./api";
import { Patient, PatientSummary, ClinicalData } from "@/types";

export const getPatients = async (
  skip = 0,
  limit = 100
): Promise<Patient[]> => {
  const response = await api.get<Patient[]>(
    `/api/v1/patients?skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const getPatient = async (id: string): Promise<Patient> => {
  const response = await api.get<Patient>(`/api/v1/patients/${id}`);
  return response.data;
};

export const createPatient = async (
  patientData: Partial<Patient>
): Promise<Patient> => {
  const response = await api.post<Patient>("/api/v1/patients", patientData);
  return response.data;
};

export const updatePatient = async (
  id: string,
  patientData: Partial<Patient>
): Promise<Patient> => {
  const response = await api.put<Patient>(
    `/api/v1/patients/${id}`,
    patientData
  );
  return response.data;
};

export const getPatientSummary = async (
  id: string
): Promise<PatientSummary> => {
  const response = await api.get<PatientSummary>(
    `/api/v1/patients/${id}/summary`
  );
  return response.data;
};

export const getPatientClinicalData = async (
  id: string,
  skip = 0,
  limit = 100
): Promise<ClinicalData[]> => {
  const response = await api.get<ClinicalData[]>(
    `/api/v1/patients/${id}/clinical-data?skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const syncPatientFromFhir = async (id: string): Promise<any> => {
  const response = await api.post(`/api/v1/patients/${id}/sync-fhir`);
  return response.data;
};

export const searchPatients = async (
  query: string,
  limit = 20
): Promise<Patient[]> => {
  const response = await api.get<Patient[]>(
    `/api/v1/patients/search?query=${encodeURIComponent(query)}&limit=${limit}`
  );
  return response.data;
};
