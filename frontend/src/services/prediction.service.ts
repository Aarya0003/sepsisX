import api from "./api";
import { SepsisPrediction } from "@/types";

export const predictSepsis = async (patientId: string): Promise<any> => {
  const response = await api.post(
    `/api/v1/predictions/predict-sepsis/${patientId}`
  );
  return response.data;
};

export const batchPredictSepsis = async (
  patientIds: string[]
): Promise<any> => {
  const response = await api.post("/api/v1/predictions/batch-predict", {
    patient_ids: patientIds,
  });
  return response.data;
};

export const getPredictionHistory = async (
  patientId: string,
  skip = 0,
  limit = 10
): Promise<SepsisPrediction[]> => {
  const response = await api.get<SepsisPrediction[]>(
    `/api/v1/predictions/history/${patientId}?skip=${skip}&limit=${limit}`
  );
  return response.data;
};

export const getPredictionDetails = async (
  predictionId: string
): Promise<any> => {
  const response = await api.get(`/api/v1/predictions/${predictionId}`);
  return response.data;
};
