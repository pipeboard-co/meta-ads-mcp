/**
 * GoHighLevel API Types
 */

export interface GHLConfig {
  apiKey: string;
  locationId?: string;
  baseUrl: string;
}

export interface GHLContact {
  id: string;
  locationId: string;
  contactName?: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  dateOfBirth?: string;
  address1?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country?: string;
  companyName?: string;
  website?: string;
  tags?: string[];
  source?: string;
  dateAdded?: string;
  dateUpdated?: string;
  customFields?: Record<string, any>;
  assignedTo?: string;
}

export interface GHLContactsResponse {
  contacts: GHLContact[];
  total: number;
  nextPage?: string;
}

export interface GHLOpportunity {
  id: string;
  locationId: string;
  name: string;
  pipelineId: string;
  pipelineStageId: string;
  assignedTo?: string;
  contactId: string;
  monetaryValue?: number;
  status: 'open' | 'won' | 'lost' | 'abandoned';
  source?: string;
  dateAdded?: string;
  dateUpdated?: string;
  lastStatusChangeAt?: string;
  customFields?: Record<string, any>;
}

export interface GHLOpportunitiesResponse {
  opportunities: GHLOpportunity[];
  total: number;
  nextPage?: string;
}

export interface GHLPipeline {
  id: string;
  locationId: string;
  name: string;
  stages: GHLPipelineStage[];
}

export interface GHLPipelineStage {
  id: string;
  name: string;
  position: number;
}

export interface GHLAPIError {
  error: string;
  message: string;
  statusCode: number;
}

export interface ContactsQueryParams {
  locationId: string;
  limit?: number;
  startAfter?: string;
  query?: string;
  tags?: string[];
}

export interface OpportunitiesQueryParams {
  locationId: string;
  pipelineId?: string;
  limit?: number;
  startAfter?: string;
  status?: 'open' | 'won' | 'lost' | 'abandoned' | 'all';
}
