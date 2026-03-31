import { useQuery } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { queryKeys } from '../utils/queryKeys';

export const useAuth = () =>
  useQuery({
    queryKey: queryKeys.me,
    queryFn: authApi.me,
    retry: false
  });
