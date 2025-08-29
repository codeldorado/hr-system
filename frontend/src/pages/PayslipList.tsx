import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Download,
  Delete,
  Visibility,
  FilterList,
  Clear,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { payslipService, Payslip } from '../services/payslipService';
import LoadingSpinner from '../components/LoadingSpinner';

const PayslipList: React.FC = () => {
  const [filters, setFilters] = useState({
    employee_id: '',
    year: '',
    month: '',
  });
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    payslip: Payslip | null;
  }>({ open: false, payslip: null });

  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: payslips = [], isLoading, error } = useQuery(
    ['payslips', filters],
    () => {
      const queryFilters: {
        employee_id?: number;
        year?: number;
        month?: number;
      } = {};
      
      if (user?.role === 'employee') {
        queryFilters.employee_id = user.employee_id;
      } else if (filters.employee_id) {
        queryFilters.employee_id = parseInt(filters.employee_id);
      }
      
      if (filters.year) queryFilters.year = parseInt(filters.year);
      if (filters.month) queryFilters.month = parseInt(filters.month);
      
      return payslipService.getPayslips(queryFilters);
    },
    {
      enabled: !!user,
    }
  );

  const deleteMutation = useMutation(
    (id: number) => payslipService.deletePayslip(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['payslips']);
        setDeleteDialog({ open: false, payslip: null });
      },
    }
  );

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const clearFilters = () => {
    setFilters({
      employee_id: '',
      year: '',
      month: '',
    });
  };

  const handleDelete = (payslip: Payslip) => {
    setDeleteDialog({ open: true, payslip });
  };

  const confirmDelete = () => {
    if (deleteDialog.payslip) {
      deleteMutation.mutate(deleteDialog.payslip.id);
    }
  };

  const handleDownload = (payslip: Payslip) => {
    window.open(payslip.file_url, '_blank');
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

  if (isLoading) {
    return <LoadingSpinner message="Loading payslips..." />;
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load payslips. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Payslips
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        View and manage your payslip records.
      </Typography>

      {/* Filters */}
      <Card sx={{ mt: 3, mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <FilterList sx={{ mr: 1 }} />
            <Typography variant="h6">Filters</Typography>
          </Box>
          <Grid container spacing={2} alignItems="center">
            {user?.role !== 'employee' && (
              <Grid item xs={12} sm={3}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={filters.employee_id}
                  onChange={(e) => handleFilterChange('employee_id', e.target.value)}
                  type="number"
                />
              </Grid>
            )}
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                select
                label="Year"
                value={filters.year}
                onChange={(e) => handleFilterChange('year', e.target.value)}
              >
                <MenuItem value="">All Years</MenuItem>
                {years.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                select
                label="Month"
                value={filters.month}
                onChange={(e) => handleFilterChange('month', e.target.value)}
              >
                <MenuItem value="">All Months</MenuItem>
                {months.map((month) => (
                  <MenuItem key={month.value} value={month.value}>
                    {month.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="outlined"
                startIcon={<Clear />}
                onClick={clearFilters}
                fullWidth
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Payslips Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {user?.role !== 'employee' && (
                <TableCell>Employee ID</TableCell>
              )}
              <TableCell>Period</TableCell>
              <TableCell>Filename</TableCell>
              <TableCell>File Size</TableCell>
              <TableCell>Upload Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {payslips.length === 0 ? (
              <TableRow>
                <TableCell 
                  colSpan={user?.role !== 'employee' ? 6 : 5} 
                  align="center"
                  sx={{ py: 4 }}
                >
                  <Typography variant="body1" color="textSecondary">
                    No payslips found. Try adjusting your filters or upload a new payslip.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              payslips.map((payslip) => (
                <TableRow key={payslip.id} hover>
                  {user?.role !== 'employee' && (
                    <TableCell>{payslip.employee_id}</TableCell>
                  )}
                  <TableCell>
                    <Chip
                      label={`${payslipService.getMonthName(payslip.month)} ${payslip.year}`}
                      variant="outlined"
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>{payslip.filename}</TableCell>
                  <TableCell>
                    {payslipService.formatFileSize(payslip.file_size)}
                  </TableCell>
                  <TableCell>
                    {payslipService.formatDate(payslip.upload_timestamp)}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      onClick={() => handleDownload(payslip)}
                      color="primary"
                      title="Download"
                    >
                      <Download />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDownload(payslip)}
                      color="info"
                      title="View"
                    >
                      <Visibility />
                    </IconButton>
                    {(user?.role === 'administrator' || user?.role === 'hr_manager') && (
                      <IconButton
                        onClick={() => handleDelete(payslip)}
                        color="error"
                        title="Delete"
                      >
                        <Delete />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, payslip: null })}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the payslip for{' '}
            {deleteDialog.payslip && 
              `${payslipService.getMonthName(deleteDialog.payslip.month)} ${deleteDialog.payslip.year}`
            }?
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialog({ open: false, payslip: null })}
            disabled={deleteMutation.isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PayslipList;
