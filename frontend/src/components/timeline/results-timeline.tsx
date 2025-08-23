'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Upload, BarChart3, FileText, MessageSquare, AlertCircle, CheckCircle } from 'lucide-react';

interface TimelineEvent {
  id: string;
  type: 'upload' | 'analysis' | 'report' | 'consultation' | 'alert' | 'milestone';
  title: string;
  description: string;
  timestamp: string;
  status: 'completed' | 'in-progress' | 'pending' | 'failed';
  metadata?: {
    fileType?: string;
    analysisType?: string;
    severity?: 'low' | 'medium' | 'high';
    [key: string]: any;
  };
}

interface ResultsTimelineProps {
  userId: string;
}

// API function to fetch real timeline events
const fetchTimelineEvents = async (userId: string): Promise<TimelineEvent[]> => {
  console.log('🔍 Fetching timeline events for user:', userId);
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  const url = `${API_BASE_URL}/api/timeline/${userId}`;
  console.log('🌐 Timeline API URL:', url);
  
  const response = await fetch(url);
  console.log('📡 Timeline API Response status:', response.status);
  
  if (!response.ok) {
    console.error('❌ Timeline API response not ok:', response.status, response.statusText);
    throw new Error(`Failed to fetch timeline events: ${response.status}`);
  }
  
  const data = await response.json();
  console.log('✅ Timeline API Response data:', data);
  console.log('📊 Total timeline events received:', data.length);
  
  // Transform backend data to frontend format
  return data.map((item: any) => ({
    id: item.id.toString(),
    type: item.event_type || 'milestone',
    title: item.title,
    description: item.description,
    timestamp: item.timestamp,
    status: item.status || 'completed',
    metadata: item.metadata || {}
  }));
};

const getEventIcon = (type: string, status: string) => {
  const baseIconClass = "h-5 w-5";
  
  switch (type) {
    case 'upload':
      return <Upload className={baseIconClass} />;
    case 'analysis':
      return <BarChart3 className={baseIconClass} />;
    case 'report':
      return <FileText className={baseIconClass} />;
    case 'consultation':
      return <MessageSquare className={baseIconClass} />;
    case 'alert':
      return <AlertCircle className={baseIconClass} />;
    case 'milestone':
      return <CheckCircle className={baseIconClass} />;
    default:
      return <CheckCircle className={baseIconClass} />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-500';
    case 'in-progress':
      return 'bg-blue-500';
    case 'pending':
      return 'bg-yellow-500';
    case 'failed':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
};

const getStatusBadgeVariant = (status: string) => {
  switch (status) {
    case 'completed':
      return 'default';
    case 'in-progress':
      return 'secondary';
    case 'pending':
      return 'outline';
    case 'failed':
      return 'destructive';
    default:
      return 'outline';
  }
};

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  return {
    date: date.toLocaleDateString(),
    time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
};

export function ResultsTimeline({ userId }: ResultsTimelineProps) {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ['timeline', userId],
    queryFn: () => fetchTimelineEvents(userId),
    enabled: !!userId,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Results Timeline</CardTitle>
          <CardDescription>Chronological view of your genomic analysis journey</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading timeline...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Results Timeline</CardTitle>
          <CardDescription>Chronological view of your genomic analysis journey</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load timeline data. Please try again later.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Results Timeline</CardTitle>
        <CardDescription>
          Track your genomic analysis progress and key milestones
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          
          <div className="space-y-6">
            {events?.map((event, index) => {
              const { date, time } = formatTimestamp(event.timestamp);
              
              return (
                <div key={event.id} className="relative flex items-start space-x-4">
                  {/* Timeline dot */}
                  <div className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-4 border-white ${getStatusColor(event.status)}`}>
                    <div className="text-white">
                      {getEventIcon(event.type, event.status)}
                    </div>
                  </div>
                  
                  {/* Event content */}
                  <div className="flex-1 min-w-0 pb-6">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {event.title}
                      </h3>
                      <Badge variant={getStatusBadgeVariant(event.status)}>
                        {event.status.replace('-', ' ').toUpperCase()}
                      </Badge>
                    </div>
                    
                    <p className="text-gray-600 mb-3">
                      {event.description}
                    </p>
                    
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <span className="font-medium">{date}</span>
                      <span className="mx-2">•</span>
                      <span>{time}</span>
                    </div>
                    
                    {/* Metadata */}
                    {event.metadata && (
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <span
                            key={key}
                            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {key.replace(/([A-Z])/g, ' $1').toLowerCase()}: {String(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        {events && events.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="mx-auto h-12 w-12 mb-4" />
            <p>No timeline events found. Upload your genomic data to get started!</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
