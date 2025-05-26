// src/services/api.js
import axios from 'axios';

export const fetchCarbonData = async () => {
  const res = await axios.get('/api/carbon'); // ✅ 이렇게 절대 상대 경로!
  return res.data;
};

export const fetchJobData = async () => {
  const res = await axios.get('/api/jobs');
  return res.data;
};

export const fetchClusterLoad = async () => {
  const res = await axios.get('/api/cluster-load');
  return res.data;
};

export const fetchScheduleData = async () => {
  const res = await axios.get('/api/schedule');
  return res.data;
};
