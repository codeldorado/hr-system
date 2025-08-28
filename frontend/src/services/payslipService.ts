import { apiService } from './api';

export interface Payslip {
  id: number;
  employee_id: number;
  month: number;
  year: number;
  filename: string;
  file_url: string;
  file_size: number;
  upload_timestamp: string;
}

export interface PayslipFilters {
  employee_id?: number;
  year?: number;
  month?: number;
  skip?: number;
  limit?: number;
}

export interface UploadPayslipRequest {
  employee_id: number;
  month: number;
  year: number;
  file: File;
}

class PayslipService {
  async getPayslips(filters?: PayslipFilters): Promise<Payslip[]> {
    return apiService.get<Payslip[]>('/payslips', filters);
  }

  async getPayslip(id: number): Promise<Payslip> {
    return apiService.get<Payslip>(`/payslips/${id}`);
  }

  async uploadPayslip(
    request: UploadPayslipRequest,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<Payslip> {
    const formData = new FormData();
    formData.append('employee_id', request.employee_id.toString());
    formData.append('month', request.month.toString());
    formData.append('year', request.year.toString());
    formData.append('file', request.file);

    return apiService.uploadFile<Payslip>('/payslips', formData, onUploadProgress);
  }

  async deletePayslip(id: number): Promise<{ message: string }> {
    return apiService.delete<{ message: string }>(`/payslips/${id}`);
  }

  // Utility methods
  getMonthName(month: number): string {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1] || 'Unknown';
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}

export const payslipService = new PayslipService();
