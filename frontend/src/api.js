import axios from "axios";
const BASE_URL = "http://192.168.8.125:8001";

export const getNodes = async () => await axios.get(`${BASE_URL}/nodes`);
export const getImages = async () => await axios.get(`${BASE_URL}/images`);
export const trainModel = async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/train`, data, {
        headers: { "Content-Type": "application/json" },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  };
  
export const runInference = async (data) => {
    const response = await axios.post(`${BASE_URL}/inference`, data, {
        headers: { "Content-Type": "application/json" },
    });
    return response;
};
