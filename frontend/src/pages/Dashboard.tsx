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
  Chip,
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
                      primary={`${payslipService.getMonthName(payslip.month)} ${payslip.year}`}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <Typography variant="body2" color="textSecondary">
                            {payslip.filename}
                          </Typography>
                          <Chip
                            label={payslipService.formatFileSize(payslip.file_size)}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="body2" color="textSecondary">
                            {payslipService.formatDate(payslip.upload_timestamp)}
                          </Typography>
                        </Box>
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
