'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Search, Eye, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { PatientListProps, Patient } from '@/types/ui-types';

// Use environment variable for API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// API function to fetch real patients
const fetchPatients = async (doctorId?: string): Promise<Patient[]> => {
  const url = doctorId 
    ? `${API_BASE_URL}/api/doctor/patients/${doctorId}`
    : `${API_BASE_URL}/api/doctor/patients`;
    
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  
  const data = await response.json();
  
  // Transform backend data to frontend format if needed
  return data.map((patient: Record<string, unknown>) => ({
    id: patient.id as string,
    name: (patient.name as string) || 'Unknown Patient',
    age: (patient.age as number) || 0,
    gender: (patient.gender as string) || 'Unknown',
    email: (patient.email as string) || '',
    lastVisit: (patient.last_visit as string) || new Date().toISOString(),
    riskLevel: (patient.risk_level as string) || 'low',
    analysisStatus: (patient.analysis_status as string) || 'pending',
    highRiskConditions: (patient.high_risk_conditions as number) || 0,
    totalConditions: (patient.total_conditions as number) || 0
  }));
};

const getRiskBadgeVariant = (riskLevel: string) => {
  switch (riskLevel) {
    case 'high':
      return 'destructive';
    case 'moderate':
      return 'secondary';
    case 'low':
      return 'default';
    default:
      return 'default';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'in-progress':
      return <Clock className="h-4 w-4 text-blue-500" />;
    case 'pending':
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    default:
      return <Clock className="h-4 w-4 text-gray-500" />;
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export function PatientList({ doctorId }: PatientListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients', doctorId],
    queryFn: fetchPatients,
  });

  const filteredPatients = patients?.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Patient List</CardTitle>
          <CardDescription>Manage and review your patients' genomic data</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading patients...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Patient List</CardTitle>
          <CardDescription>Manage and review your patients' genomic data</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load patient data. Please try again later.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Patient List</CardTitle>
        <CardDescription>
          Manage and review your patients' genomic analysis results
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search patients by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Age/Gender</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Analysis Status</TableHead>
                <TableHead>High Risk Conditions</TableHead>
                <TableHead>Last Visit</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPatients.map((patient) => (
                <TableRow key={patient.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{patient.name}</div>
                      <div className="text-sm text-gray-500">{patient.email}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div>{patient.age} years</div>
                      <div className="text-gray-500">{patient.gender}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getRiskBadgeVariant(patient.riskLevel)}>
                      {patient.riskLevel.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(patient.analysisStatus)}
                      <span className="capitalize text-sm">
                        {patient.analysisStatus.replace('-', ' ')}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <span className="font-medium text-red-600">
                        {patient.highRiskConditions}
                      </span>
                      <span className="text-gray-500">
                        /{patient.totalConditions}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-600">
                      {formatDate(patient.lastVisit)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {filteredPatients.length === 0 && searchTerm && (
          <div className="text-center py-8 text-gray-500">
            <Search className="mx-auto h-12 w-12 mb-4" />
            <p>No patients found matching "{searchTerm}"</p>
          </div>
        )}

        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredPatients.length} of {patients?.length || 0} patients
        </div>
      </CardContent>
    </Card>
  );
}
