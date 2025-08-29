import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Upload,
  Description,
  TrendingUp,
  Person,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { payslipService } from '../services/payslipService';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Utility functions
  const getMonthName = (month: number): string => {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1] || 'Unknown';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const { data: payslips = [] } = useQuery(
    ['payslips', user?.employee_id],
    () => payslipService.getPayslips({ 
      employee_id: user?.role === 'employee' ? user.employee_id : undefined,
      limit: 5 
    }),
    {
      enabled: !!user,
    }
  );

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  const stats = [
    {
      title: 'Total Payslips',
      value: payslips.length,
      icon: <Description />,
      color: 'primary',
    },
    {
      title: 'This Year',
      value: payslips.filter(p => p.year === currentYear).length,
      icon: <TrendingUp />,
      color: 'success',
    },
    {
      title: 'This Month',
      value: payslips.filter(p => p.year === currentYear && p.month === currentMonth).length,
      icon: <Person />,
      color: 'info',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome back, {user?.name}!
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        Manage your payslips and track your employment records.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Upload />}
                  onClick={() => navigate('/upload')}
                  fullWidth
                >
                  Upload Payslip
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Description />}
                  onClick={() => navigate('/payslips')}
                  fullWidth
                >
                  View All Payslips
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            {stats.map((stat, index) => (
              <Grid item xs={12} sm={4} key={index}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ mr: 1, color: `${stat.color}.main` }}>
                        {stat.icon}
                      </Box>
                      <Typography variant="h4" component="div">
                        {stat.value}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {stat.title}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Recent Payslips */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Payslips
            </Typography>
            {payslips.length > 0 ? (
              <List>
                {payslips.slice(0, 5).map((payslip) => (
                  <ListItem key={payslip.id} divider>
                    <ListItemText
                      primary={`${getMonthName(payslip.month)} ${payslip.year}`}
                      secondary={
                        <React.Fragment>
                          <span style={{ display: 'block', marginTop: '4px' }}>
                            <span style={{ marginRight: '8px', color: '#666' }}>
                              {payslip.filename}
                            </span>
                            <span style={{
                              display: 'inline-block',
                              padding: '2px 8px',
                              border: '1px solid #ccc',
                              borderRadius: '12px',
                              fontSize: '12px',
                              marginRight: '8px'
                            }}>
                              {formatFileSize(payslip.file_size)}
                            </span>
                            <span style={{ color: '#666' }}>
                              {formatDate(payslip.upload_timestamp)}
                            </span>
                          </span>
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="textSecondary">
                  No payslips found. Upload your first payslip to get started.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Upload />}
                  onClick={() => navigate('/upload')}
                  sx={{ mt: 2 }}
                >
                  Upload Payslip
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
