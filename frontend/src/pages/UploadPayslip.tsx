import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  LinearProgress,
  Grid,
  MenuItem,
  Paper,
} from '@mui/material';
import { CloudUpload, CheckCircle } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { payslipService } from '../services/payslipService';

interface UploadError {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

const UploadPayslip: React.FC = () => {
  const [employeeId, setEmployeeId] = useState('');
  const [month, setMonth] = useState('');
  const [year, setYear] = useState(new Date().getFullYear().toString());
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Set default employee ID for regular employees
  React.useEffect(() => {
    if (user?.role === 'employee') {
      setEmployeeId(user.employee_id.toString());
    }
  }, [user]);

  const uploadMutation = useMutation(
    (data: { employee_id: number; month: number; year: number; file: File }) =>
      payslipService.uploadPayslip(data, (progressEvent) => {
        const progress = progressEvent.total
          ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
          : 0;
        setUploadProgress(progress);
      }),
    {
      onSuccess: () => {
        setSuccess(true);
        setError('');
        queryClient.invalidateQueries(['payslips']);
        setTimeout(() => {
          navigate('/payslips');
        }, 2000);
      },
      onError: (error: UploadError) => {
        setError(error.response?.data?.detail || 'Upload failed');
        setUploadProgress(0);
      },
    }
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(f => f.type === 'application/pdf');
    
    if (pdfFile) {
      setFile(pdfFile);
      setError('');
    } else {
      setError('Please select a PDF file');
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please select a PDF file');
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file || !employeeId || !month || !year) {
      setError('Please fill in all fields and select a file');
      return;
    }

    uploadMutation.mutate({
      employee_id: parseInt(employeeId),
      month: parseInt(month),
      year: parseInt(year),
      file,
    });
  };

  const months = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' },
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  if (success) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Card sx={{ maxWidth: 400, textAlign: 'center' }}>
          <CardContent sx={{ p: 4 }}>
            <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Upload Successful!
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Your payslip has been uploaded successfully. Redirecting to payslips list...
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Payslip
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        Upload a PDF payslip file for record keeping.
      </Typography>

      <Card sx={{ mt: 3, maxWidth: 800 }}>
        <CardContent sx={{ p: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  required
                  disabled={user?.role === 'employee' || uploadMutation.isLoading}
                  type="number"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  select
                  label="Month"
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  required
                  disabled={uploadMutation.isLoading}
                >
                  {months.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  select
                  label="Year"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  required
                  disabled={uploadMutation.isLoading}
                >
                  {years.map((yearOption) => (
                    <MenuItem key={yearOption} value={yearOption}>
                      {yearOption}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            </Grid>

            <Paper
              className={`upload-area ${dragOver ? 'drag-over' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
              sx={{ mt: 3, p: 4, cursor: 'pointer' }}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="file-input"
                disabled={uploadMutation.isLoading}
              />
              <Box textAlign="center">
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                {file ? (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {file.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {payslipService.formatFileSize(file.size)}
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Drop your PDF file here or click to browse
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Only PDF files are accepted (max 10MB)
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>

            {uploadMutation.isLoading && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" gutterBottom>
                  Uploading... {uploadProgress}%
                </Typography>
                <LinearProgress variant="determinate" value={uploadProgress} />
              </Box>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                disabled={!file || uploadMutation.isLoading}
                startIcon={<CloudUpload />}
              >
                {uploadMutation.isLoading ? 'Uploading...' : 'Upload Payslip'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/payslips')}
                disabled={uploadMutation.isLoading}
              >
                Cancel
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UploadPayslip;
