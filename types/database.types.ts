export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      accountants: {
        Row: {
          bio: string | null
          career: Json | null
          completed_projects: number | null
          cpa_number: string | null
          cpa_type: string | null
          created_at: string | null
          current_company: string | null
          current_position: string | null
          education: Json | null
          experience_years: number | null
          id: string
          is_active: boolean | null
          license_date: string | null
          name: string
          profile_image_url: string | null
          specialties: Json | null
          total_projects: number | null
          updated_at: string | null
        }
        Insert: {
          bio?: string | null
          career?: Json | null
          completed_projects?: number | null
          cpa_number?: string | null
          cpa_type?: string | null
          created_at?: string | null
          current_company?: string | null
          current_position?: string | null
          education?: Json | null
          experience_years?: number | null
          id: string
          is_active?: boolean | null
          license_date?: string | null
          name: string
          profile_image_url?: string | null
          specialties?: Json | null
          total_projects?: number | null
          updated_at?: string | null
        }
        Update: {
          bio?: string | null
          career?: Json | null
          completed_projects?: number | null
          cpa_number?: string | null
          cpa_type?: string | null
          created_at?: string | null
          current_company?: string | null
          current_position?: string | null
          education?: Json | null
          experience_years?: number | null
          id?: string
          is_active?: boolean | null
          license_date?: string | null
          name?: string
          profile_image_url?: string | null
          specialties?: Json | null
          total_projects?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      approval_points: {
        Row: {
          ai_decision: string | null
          ai_rationale: string | null
          approval_id: number
          category: string | null
          created_at: string | null
          human_decision: string | null
          human_note: string | null
          point_code: string | null
          project_id: string | null
          question: string | null
        }
        Insert: {
          ai_decision?: string | null
          ai_rationale?: string | null
          approval_id?: number
          category?: string | null
          created_at?: string | null
          human_decision?: string | null
          human_note?: string | null
          point_code?: string | null
          project_id?: string | null
          question?: string | null
        }
        Update: {
          ai_decision?: string | null
          ai_rationale?: string | null
          approval_id?: number
          category?: string | null
          created_at?: string | null
          human_decision?: string | null
          human_note?: string | null
          point_code?: string | null
          project_id?: string | null
          question?: string | null
        }
        Relationships: []
      }
      asset_approval_points: {
        Row: {
          ai_recommended: Json | null
          ai_scenarios: Json | null
          approval_id: string
          approved_at: string | null
          approved_by: string | null
          approved_value: Json | null
          comment: string | null
          created_at: string | null
          importance: number
          point_id: string
          point_name: string
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id: string
          point_name: string
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id?: string
          point_name?: string
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "asset_approval_points_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      asset_documents: {
        Row: {
          category: string | null
          created_at: string | null
          description: string | null
          document_id: string
          extracted_data: Json | null
          file_name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          project_id: string
          upload_status: string | null
          uploaded_by: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          project_id: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          project_id?: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "asset_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      asset_drafts: {
        Row: {
          created_at: string | null
          created_by: string | null
          draft_id: string
          project_id: string
          section_1_completed: boolean | null
          section_1_summary: string | null
          section_2_completed: boolean | null
          section_2_overview: string | null
          section_3_company: string | null
          section_3_completed: boolean | null
          section_4_completed: boolean | null
          section_4_financial: string | null
          section_5_completed: boolean | null
          section_5_methodology: string | null
          section_6_completed: boolean | null
          section_6_results: string | null
          section_7_completed: boolean | null
          section_7_sensitivity: string | null
          section_8_completed: boolean | null
          section_8_conclusion: string | null
          section_9_appendix: string | null
          section_9_completed: boolean | null
          status: string | null
          submitted_at: string | null
          updated_at: string | null
          version: number | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id?: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "asset_drafts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      asset_reports: {
        Row: {
          created_at: string | null
          download_count: number | null
          draft_id: string | null
          file_size: number | null
          issued_at: string | null
          issued_by: string | null
          project_id: string
          report_id: string
          report_url: string
        }
        Insert: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id: string
          report_id?: string
          report_url: string
        }
        Update: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id?: string
          report_id?: string
          report_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "asset_reports_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "asset_drafts"
            referencedColumns: ["draft_id"]
          },
          {
            foreignKeyName: "asset_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      asset_results: {
        Row: {
          asset_adjustments: Json | null
          calculation_details: Json | null
          created_at: string | null
          created_by: string | null
          enterprise_value: number | null
          equity_value: number | null
          fair_value_adjustments: Json | null
          liability_adjustments: Json | null
          net_asset_value: number | null
          project_id: string
          result_id: string
          total_assets: number | null
          total_liabilities: number | null
          updated_at: string | null
          value_per_share: number | null
        }
        Insert: {
          asset_adjustments?: Json | null
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          fair_value_adjustments?: Json | null
          liability_adjustments?: Json | null
          net_asset_value?: number | null
          project_id: string
          result_id?: string
          total_assets?: number | null
          total_liabilities?: number | null
          updated_at?: string | null
          value_per_share?: number | null
        }
        Update: {
          asset_adjustments?: Json | null
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          fair_value_adjustments?: Json | null
          liability_adjustments?: Json | null
          net_asset_value?: number | null
          project_id?: string
          result_id?: string
          total_assets?: number | null
          total_liabilities?: number | null
          updated_at?: string | null
          value_per_share?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "asset_results_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      asset_revisions: {
        Row: {
          assigned_to: string | null
          completed_at: string | null
          created_at: string | null
          details: string
          draft_id: string
          requested_at: string | null
          requested_by: string | null
          revision_id: string
          revision_type: string
          section: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details: string
          draft_id: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details?: string
          draft_id?: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type?: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "asset_revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "asset_drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      customers: {
        Row: {
          address: string | null
          business_number: string
          ceo_name: string
          company_name: string
          company_website: string | null
          created_at: string | null
          customer_id: string
          email: string
          employees: number | null
          fax: string | null
          founded_date: string | null
          industry: string | null
          phone: string | null
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          business_number: string
          ceo_name: string
          company_name: string
          company_website?: string | null
          created_at?: string | null
          customer_id: string
          email: string
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          phone?: string | null
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          business_number?: string
          ceo_name?: string
          company_name?: string
          company_website?: string | null
          created_at?: string | null
          customer_id?: string
          email?: string
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          phone?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      dcf_approval_points: {
        Row: {
          ai_recommended: Json | null
          ai_scenarios: Json | null
          approval_id: string
          approved_at: string | null
          approved_by: string | null
          approved_value: Json | null
          comment: string | null
          created_at: string | null
          importance: number
          point_id: string
          point_name: string
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id: string
          point_name: string
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id?: string
          point_name?: string
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dcf_approval_points_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      dcf_documents: {
        Row: {
          category: string | null
          created_at: string | null
          description: string | null
          document_id: string
          extracted_data: Json | null
          file_name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          project_id: string
          upload_status: string | null
          uploaded_by: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          project_id: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          project_id?: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dcf_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      dcf_drafts: {
        Row: {
          created_at: string | null
          created_by: string | null
          draft_id: string
          project_id: string
          section_1_completed: boolean | null
          section_1_summary: string | null
          section_2_completed: boolean | null
          section_2_overview: string | null
          section_3_company: string | null
          section_3_completed: boolean | null
          section_4_completed: boolean | null
          section_4_financial: string | null
          section_5_completed: boolean | null
          section_5_methodology: string | null
          section_6_completed: boolean | null
          section_6_results: string | null
          section_7_completed: boolean | null
          section_7_sensitivity: string | null
          section_8_completed: boolean | null
          section_8_conclusion: string | null
          section_9_appendix: string | null
          section_9_completed: boolean | null
          status: string | null
          submitted_at: string | null
          updated_at: string | null
          version: number | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id?: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "dcf_drafts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      dcf_reports: {
        Row: {
          created_at: string | null
          download_count: number | null
          draft_id: string | null
          file_size: number | null
          issued_at: string | null
          issued_by: string | null
          project_id: string
          report_id: string
          report_url: string
        }
        Insert: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id: string
          report_id?: string
          report_url: string
        }
        Update: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id?: string
          report_id?: string
          report_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "dcf_reports_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "dcf_drafts"
            referencedColumns: ["draft_id"]
          },
          {
            foreignKeyName: "dcf_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      dcf_results: {
        Row: {
          calculation_details: Json | null
          created_at: string | null
          created_by: string | null
          enterprise_value: number | null
          equity_value: number | null
          free_cash_flows: Json | null
          project_id: string
          projection_years: number | null
          result_id: string
          sensitivity_matrix: Json | null
          terminal_growth_rate: number | null
          terminal_value: number | null
          updated_at: string | null
          value_per_share: number | null
          wacc: number | null
        }
        Insert: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          free_cash_flows?: Json | null
          project_id: string
          projection_years?: number | null
          result_id?: string
          sensitivity_matrix?: Json | null
          terminal_growth_rate?: number | null
          terminal_value?: number | null
          updated_at?: string | null
          value_per_share?: number | null
          wacc?: number | null
        }
        Update: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          free_cash_flows?: Json | null
          project_id?: string
          projection_years?: number | null
          result_id?: string
          sensitivity_matrix?: Json | null
          terminal_growth_rate?: number | null
          terminal_value?: number | null
          updated_at?: string | null
          value_per_share?: number | null
          wacc?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "dcf_results_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      dcf_revisions: {
        Row: {
          assigned_to: string | null
          completed_at: string | null
          created_at: string | null
          details: string
          draft_id: string
          requested_at: string | null
          requested_by: string | null
          revision_id: string
          revision_type: string
          section: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details: string
          draft_id: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details?: string
          draft_id?: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type?: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "dcf_revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "dcf_drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      deal_news: {
        Row: {
          company_name: string
          created_at: string | null
          id: string
          industry: string | null
          investment_amount: number | null
          investment_stage: string | null
          investor_names: string[] | null
          published_at: string | null
          region: string | null
          source_url: string | null
        }
        Insert: {
          company_name: string
          created_at?: string | null
          id?: string
          industry?: string | null
          investment_amount?: number | null
          investment_stage?: string | null
          investor_names?: string[] | null
          published_at?: string | null
          region?: string | null
          source_url?: string | null
        }
        Update: {
          company_name?: string
          created_at?: string | null
          id?: string
          industry?: string | null
          investment_amount?: number | null
          investment_stage?: string | null
          investor_names?: string[] | null
          published_at?: string | null
          region?: string | null
          source_url?: string | null
        }
        Relationships: []
      }
      deals: {
        Row: {
          amount: number | null
          ceo: string | null
          company_name: string
          created_at: string | null
          founded: string | null
          id: number
          industry: string | null
          industry_category: string | null
          investment_reason: string | null
          investors: string | null
          location: string | null
          news_date: string | null
          news_title: string | null
          news_url: string | null
          number: number | null
          site_name: string | null
          stage: string | null
          total_funding: number | null
          updated_at: string | null
        }
        Insert: {
          amount?: number | null
          ceo?: string | null
          company_name: string
          created_at?: string | null
          founded?: string | null
          id?: number
          industry?: string | null
          industry_category?: string | null
          investment_reason?: string | null
          investors?: string | null
          location?: string | null
          news_date?: string | null
          news_title?: string | null
          news_url?: string | null
          number?: number | null
          site_name?: string | null
          stage?: string | null
          total_funding?: number | null
          updated_at?: string | null
        }
        Update: {
          amount?: number | null
          ceo?: string | null
          company_name?: string
          created_at?: string | null
          founded?: string | null
          id?: number
          industry?: string | null
          industry_category?: string | null
          investment_reason?: string | null
          investors?: string | null
          location?: string | null
          news_date?: string | null
          news_title?: string | null
          news_url?: string | null
          number?: number | null
          site_name?: string | null
          stage?: string | null
          total_funding?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      documents: {
        Row: {
          document_id: number
          file_name: string | null
          file_type: string | null
          file_url: string | null
          project_id: string | null
          upload_status: string | null
          uploaded_at: string | null
        }
        Insert: {
          document_id?: number
          file_name?: string | null
          file_type?: string | null
          file_url?: string | null
          project_id?: string | null
          upload_status?: string | null
          uploaded_at?: string | null
        }
        Update: {
          document_id?: number
          file_name?: string | null
          file_type?: string | null
          file_url?: string | null
          project_id?: string | null
          upload_status?: string | null
          uploaded_at?: string | null
        }
        Relationships: []
      }
      drafts: {
        Row: {
          content: string | null
          created_at: string | null
          created_by: string | null
          draft_id: number
          project_id: string | null
          version: number | null
        }
        Insert: {
          content?: string | null
          created_at?: string | null
          created_by?: string | null
          draft_id?: number
          project_id?: string | null
          version?: number | null
        }
        Update: {
          content?: string | null
          created_at?: string | null
          created_by?: string | null
          draft_id?: number
          project_id?: string | null
          version?: number | null
        }
        Relationships: []
      }
      email_send_log: {
        Row: {
          created_at: string | null
          deals_count: number | null
          deals_ids: number[] | null
          email_type: string
          error_message: string | null
          id: number
          sent_at: string | null
          status: string
          subject: string
          subscriber_id: number
        }
        Insert: {
          created_at?: string | null
          deals_count?: number | null
          deals_ids?: number[] | null
          email_type: string
          error_message?: string | null
          id?: number
          sent_at?: string | null
          status: string
          subject: string
          subscriber_id: number
        }
        Update: {
          created_at?: string | null
          deals_count?: number | null
          deals_ids?: number[] | null
          email_type?: string
          error_message?: string | null
          id?: number
          sent_at?: string | null
          status?: string
          subject?: string
          subscriber_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "email_send_log_subscriber_id_fkey"
            columns: ["subscriber_id"]
            isOneToOne: false
            referencedRelation: "email_subscribers"
            referencedColumns: ["id"]
          },
        ]
      }
      email_subscribers: {
        Row: {
          created_at: string | null
          daily_news: boolean | null
          email: string
          email_verified: boolean | null
          id: number
          is_active: boolean | null
          last_sent_at: string | null
          name: string | null
          subscribed_at: string | null
          unsubscribed_at: string | null
          updated_at: string | null
          verification_token: string | null
          weekly_insight: boolean | null
        }
        Insert: {
          created_at?: string | null
          daily_news?: boolean | null
          email: string
          email_verified?: boolean | null
          id?: number
          is_active?: boolean | null
          last_sent_at?: string | null
          name?: string | null
          subscribed_at?: string | null
          unsubscribed_at?: string | null
          updated_at?: string | null
          verification_token?: string | null
          weekly_insight?: boolean | null
        }
        Update: {
          created_at?: string | null
          daily_news?: boolean | null
          email?: string
          email_verified?: boolean | null
          id?: number
          is_active?: boolean | null
          last_sent_at?: string | null
          name?: string | null
          subscribed_at?: string | null
          unsubscribed_at?: string | null
          updated_at?: string | null
          verification_token?: string | null
          weekly_insight?: boolean | null
        }
        Relationships: []
      }
      email_templates: {
        Row: {
          body: string | null
          company_id: number | null
          created_at: string | null
          generation_prompt: string | null
          id: number
          is_active: boolean | null
          subject: string | null
          template_type: string | null
          version: number | null
        }
        Insert: {
          body?: string | null
          company_id?: number | null
          created_at?: string | null
          generation_prompt?: string | null
          id?: number
          is_active?: boolean | null
          subject?: string | null
          template_type?: string | null
          version?: number | null
        }
        Update: {
          body?: string | null
          company_id?: number | null
          created_at?: string | null
          generation_prompt?: string | null
          id?: number
          is_active?: boolean | null
          subject?: string | null
          template_type?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "email_templates_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "startup_companies"
            referencedColumns: ["id"]
          },
        ]
      }
      evaluation_requests: {
        Row: {
          address: string | null
          admin_comment: string | null
          admin_id: string | null
          budget_max: number | null
          budget_min: number | null
          business_registration_number: string | null
          company_name_en: string | null
          company_name_kr: string
          company_website: string | null
          created_at: string | null
          employees: number | null
          fax: string | null
          founded_date: string | null
          industry: string | null
          phone: string | null
          representative_name: string | null
          request_id: string
          requested_methods: string[] | null
          requirements: string | null
          revenue: number | null
          reviewed_at: string | null
          status: string
          target_date: string | null
          updated_at: string | null
          user_id: string
          valuation_purpose: string | null
        }
        Insert: {
          address?: string | null
          admin_comment?: string | null
          admin_id?: string | null
          budget_max?: number | null
          budget_min?: number | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr: string
          company_website?: string | null
          created_at?: string | null
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          phone?: string | null
          representative_name?: string | null
          request_id?: string
          requested_methods?: string[] | null
          requirements?: string | null
          revenue?: number | null
          reviewed_at?: string | null
          status?: string
          target_date?: string | null
          updated_at?: string | null
          user_id: string
          valuation_purpose?: string | null
        }
        Update: {
          address?: string | null
          admin_comment?: string | null
          admin_id?: string | null
          budget_max?: number | null
          budget_min?: number | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr?: string
          company_website?: string | null
          created_at?: string | null
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          phone?: string | null
          representative_name?: string | null
          request_id?: string
          requested_methods?: string[] | null
          requirements?: string | null
          revenue?: number | null
          reviewed_at?: string | null
          status?: string
          target_date?: string | null
          updated_at?: string | null
          user_id?: string
          valuation_purpose?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "evaluation_requests_admin_id_fkey"
            columns: ["admin_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
          {
            foreignKeyName: "evaluation_requests_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      intrinsic_approval_points: {
        Row: {
          ai_recommended: Json | null
          ai_scenarios: Json | null
          approval_id: string
          approved_at: string | null
          approved_by: string | null
          approved_value: Json | null
          comment: string | null
          created_at: string | null
          importance: number
          point_id: string
          point_name: string
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id: string
          point_name: string
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id?: string
          point_name?: string
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_approval_points_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      intrinsic_documents: {
        Row: {
          category: string | null
          created_at: string | null
          description: string | null
          document_id: string
          extracted_data: Json | null
          file_name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          project_id: string
          upload_status: string | null
          uploaded_by: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          project_id: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          project_id?: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      intrinsic_drafts: {
        Row: {
          created_at: string | null
          created_by: string | null
          draft_id: string
          project_id: string
          section_1_completed: boolean | null
          section_1_summary: string | null
          section_2_completed: boolean | null
          section_2_overview: string | null
          section_3_company: string | null
          section_3_completed: boolean | null
          section_4_completed: boolean | null
          section_4_financial: string | null
          section_5_completed: boolean | null
          section_5_methodology: string | null
          section_6_completed: boolean | null
          section_6_results: string | null
          section_7_completed: boolean | null
          section_7_sensitivity: string | null
          section_8_completed: boolean | null
          section_8_conclusion: string | null
          section_9_appendix: string | null
          section_9_completed: boolean | null
          status: string | null
          submitted_at: string | null
          updated_at: string | null
          version: number | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id?: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_drafts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      intrinsic_reports: {
        Row: {
          created_at: string | null
          download_count: number | null
          draft_id: string | null
          file_size: number | null
          issued_at: string | null
          issued_by: string | null
          project_id: string
          report_id: string
          report_url: string
        }
        Insert: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id: string
          report_id?: string
          report_url: string
        }
        Update: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id?: string
          report_id?: string
          report_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_reports_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "intrinsic_drafts"
            referencedColumns: ["draft_id"]
          },
          {
            foreignKeyName: "intrinsic_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      intrinsic_results: {
        Row: {
          calculation_details: Json | null
          created_at: string | null
          created_by: string | null
          earnings_value: number | null
          enterprise_value: number | null
          equity_value: number | null
          net_asset_value: number | null
          project_id: string
          result_id: string
          updated_at: string | null
          value_per_share: number | null
          weight_asset: number | null
          weight_earnings: number | null
        }
        Insert: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          earnings_value?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          net_asset_value?: number | null
          project_id: string
          result_id?: string
          updated_at?: string | null
          value_per_share?: number | null
          weight_asset?: number | null
          weight_earnings?: number | null
        }
        Update: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          earnings_value?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          net_asset_value?: number | null
          project_id?: string
          result_id?: string
          updated_at?: string | null
          value_per_share?: number | null
          weight_asset?: number | null
          weight_earnings?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_results_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      intrinsic_revisions: {
        Row: {
          assigned_to: string | null
          completed_at: string | null
          created_at: string | null
          details: string
          draft_id: string
          requested_at: string | null
          requested_by: string | null
          revision_id: string
          revision_type: string
          section: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details: string
          draft_id: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details?: string
          draft_id?: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type?: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "intrinsic_revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "intrinsic_drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      investment_news: {
        Row: {
          ai_extracted_data: Json | null
          collection_id: number | null
          company_id: number | null
          content: string | null
          created_at: string | null
          id: number
          published_date: string | null
          source: string | null
          source_url: string | null
          summary: string | null
          title: string
        }
        Insert: {
          ai_extracted_data?: Json | null
          collection_id?: number | null
          company_id?: number | null
          content?: string | null
          created_at?: string | null
          id?: number
          published_date?: string | null
          source?: string | null
          source_url?: string | null
          summary?: string | null
          title: string
        }
        Update: {
          ai_extracted_data?: Json | null
          collection_id?: number | null
          company_id?: number | null
          content?: string | null
          created_at?: string | null
          id?: number
          published_date?: string | null
          source?: string | null
          source_url?: string | null
          summary?: string | null
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "investment_news_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "startup_companies"
            referencedColumns: ["id"]
          },
        ]
      }
      investment_news_articles: {
        Row: {
          article_title: string
          article_url: string
          collected_at: string | null
          content_snippet: string | null
          has_amount: boolean | null
          has_employees: boolean | null
          has_industry: boolean | null
          has_investors: boolean | null
          has_location: boolean | null
          has_stage: boolean | null
          id: number
          published_date: string
          score: number | null
          site_name: string
          site_number: number
          site_url: string
        }
        Insert: {
          article_title: string
          article_url: string
          collected_at?: string | null
          content_snippet?: string | null
          has_amount?: boolean | null
          has_employees?: boolean | null
          has_industry?: boolean | null
          has_investors?: boolean | null
          has_location?: boolean | null
          has_stage?: boolean | null
          id?: number
          published_date: string
          score?: number | null
          site_name: string
          site_number: number
          site_url: string
        }
        Update: {
          article_title?: string
          article_url?: string
          collected_at?: string | null
          content_snippet?: string | null
          has_amount?: boolean | null
          has_employees?: boolean | null
          has_industry?: boolean | null
          has_investors?: boolean | null
          has_location?: boolean | null
          has_stage?: boolean | null
          id?: number
          published_date?: string
          score?: number | null
          site_name?: string
          site_number?: number
          site_url?: string
        }
        Relationships: []
      }
      investment_news_network_sources: {
        Row: {
          category: string
          collection_method: string
          created_at: string | null
          expected_daily_count: number | null
          id: number
          is_active: boolean | null
          last_collected_at: string | null
          rank: number
          rss_url: string | null
          selector: string | null
          source_name: string
          source_number: number
          source_url: string
          updated_at: string | null
        }
        Insert: {
          category: string
          collection_method: string
          created_at?: string | null
          expected_daily_count?: number | null
          id?: number
          is_active?: boolean | null
          last_collected_at?: string | null
          rank: number
          rss_url?: string | null
          selector?: string | null
          source_name: string
          source_number: number
          source_url: string
          updated_at?: string | null
        }
        Update: {
          category?: string
          collection_method?: string
          created_at?: string | null
          expected_daily_count?: number | null
          id?: number
          is_active?: boolean | null
          last_collected_at?: string | null
          rank?: number
          rss_url?: string | null
          selector?: string | null
          source_name?: string
          source_number?: number
          source_url?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      investment_news_ranking: {
        Row: {
          id: number
          last_updated: string | null
          news_count: number | null
          period_end: string | null
          period_start: string | null
          rank: number | null
          site_name: string
          site_number: number
          site_url: string
        }
        Insert: {
          id?: number
          last_updated?: string | null
          news_count?: number | null
          period_end?: string | null
          period_start?: string | null
          rank?: number | null
          site_name: string
          site_number: number
          site_url: string
        }
        Update: {
          id?: number
          last_updated?: string | null
          news_count?: number | null
          period_end?: string | null
          period_start?: string | null
          rank?: number | null
          site_name?: string
          site_number?: number
          site_url?: string
        }
        Relationships: []
      }
      investment_rounds: {
        Row: {
          amount_krw: number | null
          announced_date: string | null
          co_investors: Json | null
          company_id: number | null
          created_at: string | null
          id: number
          investors: string | null
          lead_investor: string | null
          round_name: string | null
          source_url: string | null
          valuation_krw: number | null
        }
        Insert: {
          amount_krw?: number | null
          announced_date?: string | null
          co_investors?: Json | null
          company_id?: number | null
          created_at?: string | null
          id?: number
          investors?: string | null
          lead_investor?: string | null
          round_name?: string | null
          source_url?: string | null
          valuation_krw?: number | null
        }
        Update: {
          amount_krw?: number | null
          announced_date?: string | null
          co_investors?: Json | null
          company_id?: number | null
          created_at?: string | null
          id?: number
          investors?: string | null
          lead_investor?: string | null
          round_name?: string | null
          source_url?: string | null
          valuation_krw?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "investment_rounds_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "startup_companies"
            referencedColumns: ["id"]
          },
        ]
      }
      investor_watchlist: {
        Row: {
          company_name: string
          created_at: string | null
          id: string
          industry: string | null
          last_deal_date: string | null
          notes: string | null
          total_funding: number | null
          updated_at: string | null
          user_id: string
        }
        Insert: {
          company_name: string
          created_at?: string | null
          id?: string
          industry?: string | null
          last_deal_date?: string | null
          notes?: string | null
          total_funding?: number | null
          updated_at?: string | null
          user_id: string
        }
        Update: {
          company_name?: string
          created_at?: string | null
          id?: string
          industry?: string | null
          last_deal_date?: string | null
          notes?: string | null
          total_funding?: number | null
          updated_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "investor_watchlist_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      negotiations: {
        Row: {
          created_at: string | null
          details: string | null
          negotiation_id: number
          project_id: string | null
          request_type: string | null
          status: string | null
        }
        Insert: {
          created_at?: string | null
          details?: string | null
          negotiation_id?: number
          project_id?: string | null
          request_type?: string | null
          status?: string | null
        }
        Update: {
          created_at?: string | null
          details?: string | null
          negotiation_id?: number
          project_id?: string | null
          request_type?: string | null
          status?: string | null
        }
        Relationships: []
      }
      newsletter_subscribers: {
        Row: {
          company: string | null
          email: string
          id: string
          is_active: boolean | null
          name: string | null
          subscribed_at: string | null
          subscription_type: string | null
          unsubscribed_at: string | null
        }
        Insert: {
          company?: string | null
          email: string
          id?: string
          is_active?: boolean | null
          name?: string | null
          subscribed_at?: string | null
          subscription_type?: string | null
          unsubscribed_at?: string | null
        }
        Update: {
          company?: string | null
          email?: string
          id?: string
          is_active?: boolean | null
          name?: string | null
          subscribed_at?: string | null
          subscription_type?: string | null
          unsubscribed_at?: string | null
        }
        Relationships: []
      }
      partner_referrals: {
        Row: {
          commission_amount: number | null
          commission_status: string | null
          converted_at: string | null
          created_at: string | null
          id: string
          notes: string | null
          partner_id: string
          referred_at: string | null
          referred_company_name: string | null
          referred_email: string | null
          status: string
          updated_at: string | null
        }
        Insert: {
          commission_amount?: number | null
          commission_status?: string | null
          converted_at?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          partner_id: string
          referred_at?: string | null
          referred_company_name?: string | null
          referred_email?: string | null
          status?: string
          updated_at?: string | null
        }
        Update: {
          commission_amount?: number | null
          commission_status?: string | null
          converted_at?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          partner_id?: string
          referred_at?: string | null
          referred_company_name?: string | null
          referred_email?: string | null
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "partner_referrals_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      project_history: {
        Row: {
          accountant_id: string | null
          address: string | null
          business_registration_number: string | null
          company_name_en: string | null
          company_name_kr: string
          company_website: string | null
          completed_at: string | null
          completed_methods: string[] | null
          created_at: string | null
          fax: string | null
          final_values: Json | null
          history_id: string
          industry: string | null
          phone: string | null
          project_id: string
          representative_name: string | null
          request_id: string | null
          total_paid: number | null
          user_id: string
          valuation_purpose: string | null
        }
        Insert: {
          accountant_id?: string | null
          address?: string | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr: string
          company_website?: string | null
          completed_at?: string | null
          completed_methods?: string[] | null
          created_at?: string | null
          fax?: string | null
          final_values?: Json | null
          history_id?: string
          industry?: string | null
          phone?: string | null
          project_id: string
          representative_name?: string | null
          request_id?: string | null
          total_paid?: number | null
          user_id: string
          valuation_purpose?: string | null
        }
        Update: {
          accountant_id?: string | null
          address?: string | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr?: string
          company_website?: string | null
          completed_at?: string | null
          completed_methods?: string[] | null
          created_at?: string | null
          fax?: string | null
          final_values?: Json | null
          history_id?: string
          industry?: string | null
          phone?: string | null
          project_id?: string
          representative_name?: string | null
          request_id?: string | null
          total_paid?: number | null
          user_id?: string
          valuation_purpose?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "project_history_accountant_id_fkey"
            columns: ["accountant_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
          {
            foreignKeyName: "project_history_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      projects: {
        Row: {
          accountant_id: string | null
          address: string | null
          agreed_price: number | null
          balance_paid_at: string | null
          budget_max: number | null
          budget_min: number | null
          business_registration_number: string | null
          company_name_en: string | null
          company_name_kr: string
          company_website: string | null
          created_at: string | null
          current_step: number | null
          deposit_amount: number | null
          deposit_paid_at: string | null
          employees: number | null
          fax: string | null
          founded_date: string | null
          industry: string | null
          method: string | null
          phone: string | null
          project_id: string
          representative_name: string | null
          request_id: string | null
          requested_methods: string[] | null
          requirements: string | null
          revenue: number | null
          status: string
          target_date: string | null
          updated_at: string | null
          user_id: string
          valuation_purpose: string | null
        }
        Insert: {
          accountant_id?: string | null
          address?: string | null
          agreed_price?: number | null
          balance_paid_at?: string | null
          budget_max?: number | null
          budget_min?: number | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr: string
          company_website?: string | null
          created_at?: string | null
          current_step?: number | null
          deposit_amount?: number | null
          deposit_paid_at?: string | null
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          method?: string | null
          phone?: string | null
          project_id: string
          representative_name?: string | null
          request_id?: string | null
          requested_methods?: string[] | null
          requirements?: string | null
          revenue?: number | null
          status?: string
          target_date?: string | null
          updated_at?: string | null
          user_id: string
          valuation_purpose?: string | null
        }
        Update: {
          accountant_id?: string | null
          address?: string | null
          agreed_price?: number | null
          balance_paid_at?: string | null
          budget_max?: number | null
          budget_min?: number | null
          business_registration_number?: string | null
          company_name_en?: string | null
          company_name_kr?: string
          company_website?: string | null
          created_at?: string | null
          current_step?: number | null
          deposit_amount?: number | null
          deposit_paid_at?: string | null
          employees?: number | null
          fax?: string | null
          founded_date?: string | null
          industry?: string | null
          method?: string | null
          phone?: string | null
          project_id?: string
          representative_name?: string | null
          request_id?: string | null
          requested_methods?: string[] | null
          requirements?: string | null
          revenue?: number | null
          status?: string
          target_date?: string | null
          updated_at?: string | null
          user_id?: string
          valuation_purpose?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "projects_accountant_id_fkey"
            columns: ["accountant_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
          {
            foreignKeyName: "projects_request_id_fkey"
            columns: ["request_id"]
            isOneToOne: false
            referencedRelation: "evaluation_requests"
            referencedColumns: ["request_id"]
          },
          {
            foreignKeyName: "projects_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      projects_legacy: {
        Row: {
          company_name: string
          created_at: string | null
          current_step: number
          customer_id: string
          project_id: string
          status: string
          updated_at: string | null
          valuation_method: string
        }
        Insert: {
          company_name: string
          created_at?: string | null
          current_step?: number
          customer_id: string
          project_id: string
          status?: string
          updated_at?: string | null
          valuation_method: string
        }
        Update: {
          company_name?: string
          created_at?: string | null
          current_step?: number
          customer_id?: string
          project_id?: string
          status?: string
          updated_at?: string | null
          valuation_method?: string
        }
        Relationships: [
          {
            foreignKeyName: "projects_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["customer_id"]
          },
        ]
      }
      quotes: {
        Row: {
          base_fee: number | null
          created_at: string | null
          discount_rate: number | null
          final_fee: number | null
          payment_terms: string | null
          project_id: string | null
          quote_id: number
          sent_at: string | null
          valid_until: string | null
        }
        Insert: {
          base_fee?: number | null
          created_at?: string | null
          discount_rate?: number | null
          final_fee?: number | null
          payment_terms?: string | null
          project_id?: string | null
          quote_id?: number
          sent_at?: string | null
          valid_until?: string | null
        }
        Update: {
          base_fee?: number | null
          created_at?: string | null
          discount_rate?: number | null
          final_fee?: number | null
          payment_terms?: string | null
          project_id?: string | null
          quote_id?: number
          sent_at?: string | null
          valid_until?: string | null
        }
        Relationships: []
      }
      relative_approval_points: {
        Row: {
          ai_recommended: Json | null
          ai_scenarios: Json | null
          approval_id: string
          approved_at: string | null
          approved_by: string | null
          approved_value: Json | null
          comment: string | null
          created_at: string | null
          importance: number
          point_id: string
          point_name: string
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id: string
          point_name: string
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id?: string
          point_name?: string
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "relative_approval_points_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      relative_documents: {
        Row: {
          category: string | null
          created_at: string | null
          description: string | null
          document_id: string
          extracted_data: Json | null
          file_name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          project_id: string
          upload_status: string | null
          uploaded_by: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          project_id: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          project_id?: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "relative_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      relative_drafts: {
        Row: {
          created_at: string | null
          created_by: string | null
          draft_id: string
          project_id: string
          section_1_completed: boolean | null
          section_1_summary: string | null
          section_2_completed: boolean | null
          section_2_overview: string | null
          section_3_company: string | null
          section_3_completed: boolean | null
          section_4_completed: boolean | null
          section_4_financial: string | null
          section_5_completed: boolean | null
          section_5_methodology: string | null
          section_6_completed: boolean | null
          section_6_results: string | null
          section_7_completed: boolean | null
          section_7_sensitivity: string | null
          section_8_completed: boolean | null
          section_8_conclusion: string | null
          section_9_appendix: string | null
          section_9_completed: boolean | null
          status: string | null
          submitted_at: string | null
          updated_at: string | null
          version: number | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id?: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "relative_drafts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      relative_reports: {
        Row: {
          created_at: string | null
          download_count: number | null
          draft_id: string | null
          file_size: number | null
          issued_at: string | null
          issued_by: string | null
          project_id: string
          report_id: string
          report_url: string
        }
        Insert: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id: string
          report_id?: string
          report_url: string
        }
        Update: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id?: string
          report_id?: string
          report_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "relative_reports_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "relative_drafts"
            referencedColumns: ["draft_id"]
          },
          {
            foreignKeyName: "relative_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      relative_results: {
        Row: {
          calculation_details: Json | null
          created_at: string | null
          created_by: string | null
          enterprise_value: number | null
          equity_value: number | null
          evebitda_value: number | null
          pbr_value: number | null
          peer_companies: Json | null
          per_value: number | null
          project_id: string
          psr_value: number | null
          result_id: string
          selected_multiples: Json | null
          updated_at: string | null
          value_per_share: number | null
        }
        Insert: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          evebitda_value?: number | null
          pbr_value?: number | null
          peer_companies?: Json | null
          per_value?: number | null
          project_id: string
          psr_value?: number | null
          result_id?: string
          selected_multiples?: Json | null
          updated_at?: string | null
          value_per_share?: number | null
        }
        Update: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          evebitda_value?: number | null
          pbr_value?: number | null
          peer_companies?: Json | null
          per_value?: number | null
          project_id?: string
          psr_value?: number | null
          result_id?: string
          selected_multiples?: Json | null
          updated_at?: string | null
          value_per_share?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "relative_results_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      relative_revisions: {
        Row: {
          assigned_to: string | null
          completed_at: string | null
          created_at: string | null
          details: string
          draft_id: string
          requested_at: string | null
          requested_by: string | null
          revision_id: string
          revision_type: string
          section: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details: string
          draft_id: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details?: string
          draft_id?: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type?: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "relative_revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "relative_drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      reports: {
        Row: {
          issued_at: string | null
          project_id: string | null
          report_id: number
          report_url: string | null
        }
        Insert: {
          issued_at?: string | null
          project_id?: string | null
          report_id?: number
          report_url?: string | null
        }
        Update: {
          issued_at?: string | null
          project_id?: string | null
          report_id?: number
          report_url?: string | null
        }
        Relationships: []
      }
      revisions: {
        Row: {
          details: string | null
          draft_id: number | null
          project_id: string | null
          requested_at: string | null
          revision_id: number
          revision_type: string | null
        }
        Insert: {
          details?: string | null
          draft_id?: number | null
          project_id?: string | null
          requested_at?: string | null
          revision_id?: number
          revision_type?: string | null
        }
        Update: {
          details?: string | null
          draft_id?: number | null
          project_id?: string | null
          requested_at?: string | null
          revision_id?: number
          revision_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      startup_companies: {
        Row: {
          ceo_name: string | null
          created_at: string | null
          cumulative_funding_krw: number | null
          description: string | null
          employee_count: number | null
          founded_year: number | null
          headquarters: string | null
          id: number
          industry: string | null
          investment_stage: string | null
          latest_round_date: string | null
          latest_stage: string | null
          latest_valuation_krw: number | null
          logo_url: string | null
          name_en: string | null
          name_ko: string
          region: string | null
          sub_industry: string | null
          total_funding_krw: number | null
          updated_at: string | null
          website: string | null
          website_url: string | null
        }
        Insert: {
          ceo_name?: string | null
          created_at?: string | null
          cumulative_funding_krw?: number | null
          description?: string | null
          employee_count?: number | null
          founded_year?: number | null
          headquarters?: string | null
          id?: number
          industry?: string | null
          investment_stage?: string | null
          latest_round_date?: string | null
          latest_stage?: string | null
          latest_valuation_krw?: number | null
          logo_url?: string | null
          name_en?: string | null
          name_ko: string
          region?: string | null
          sub_industry?: string | null
          total_funding_krw?: number | null
          updated_at?: string | null
          website?: string | null
          website_url?: string | null
        }
        Update: {
          ceo_name?: string | null
          created_at?: string | null
          cumulative_funding_krw?: number | null
          description?: string | null
          employee_count?: number | null
          founded_year?: number | null
          headquarters?: string | null
          id?: number
          industry?: string | null
          investment_stage?: string | null
          latest_round_date?: string | null
          latest_stage?: string | null
          latest_valuation_krw?: number | null
          logo_url?: string | null
          name_en?: string | null
          name_ko?: string
          region?: string | null
          sub_industry?: string | null
          total_funding_krw?: number | null
          updated_at?: string | null
          website?: string | null
          website_url?: string | null
        }
        Relationships: []
      }
      support_cases: {
        Row: {
          assigned_at: string | null
          category: string | null
          created_at: string | null
          description: string | null
          id: string
          priority: string | null
          requester_email: string | null
          requester_name: string | null
          resolution_note: string | null
          resolved_at: string | null
          status: string
          supporter_id: string
          title: string
          updated_at: string | null
        }
        Insert: {
          assigned_at?: string | null
          category?: string | null
          created_at?: string | null
          description?: string | null
          id?: string
          priority?: string | null
          requester_email?: string | null
          requester_name?: string | null
          resolution_note?: string | null
          resolved_at?: string | null
          status?: string
          supporter_id: string
          title: string
          updated_at?: string | null
        }
        Update: {
          assigned_at?: string | null
          category?: string | null
          created_at?: string | null
          description?: string | null
          id?: string
          priority?: string | null
          requester_email?: string | null
          requester_name?: string | null
          resolution_note?: string | null
          resolved_at?: string | null
          status?: string
          supporter_id?: string
          title?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "support_cases_supporter_id_fkey"
            columns: ["supporter_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      tax_approval_points: {
        Row: {
          ai_recommended: Json | null
          ai_scenarios: Json | null
          approval_id: string
          approved_at: string | null
          approved_by: string | null
          approved_value: Json | null
          comment: string | null
          created_at: string | null
          importance: number
          point_id: string
          point_name: string
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id: string
          point_name: string
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          ai_recommended?: Json | null
          ai_scenarios?: Json | null
          approval_id?: string
          approved_at?: string | null
          approved_by?: string | null
          approved_value?: Json | null
          comment?: string | null
          created_at?: string | null
          importance?: number
          point_id?: string
          point_name?: string
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "tax_approval_points_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      tax_documents: {
        Row: {
          category: string | null
          created_at: string | null
          description: string | null
          document_id: string
          extracted_data: Json | null
          file_name: string
          file_path: string
          file_size: number | null
          file_type: string | null
          project_id: string
          upload_status: string | null
          uploaded_by: string | null
        }
        Insert: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name: string
          file_path: string
          file_size?: number | null
          file_type?: string | null
          project_id: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Update: {
          category?: string | null
          created_at?: string | null
          description?: string | null
          document_id?: string
          extracted_data?: Json | null
          file_name?: string
          file_path?: string
          file_size?: number | null
          file_type?: string | null
          project_id?: string
          upload_status?: string | null
          uploaded_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "tax_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      tax_drafts: {
        Row: {
          created_at: string | null
          created_by: string | null
          draft_id: string
          project_id: string
          section_1_completed: boolean | null
          section_1_summary: string | null
          section_2_completed: boolean | null
          section_2_overview: string | null
          section_3_company: string | null
          section_3_completed: boolean | null
          section_4_completed: boolean | null
          section_4_financial: string | null
          section_5_completed: boolean | null
          section_5_methodology: string | null
          section_6_completed: boolean | null
          section_6_results: string | null
          section_7_completed: boolean | null
          section_7_sensitivity: string | null
          section_8_completed: boolean | null
          section_8_conclusion: string | null
          section_9_appendix: string | null
          section_9_completed: boolean | null
          status: string | null
          submitted_at: string | null
          updated_at: string | null
          version: number | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          draft_id?: string
          project_id?: string
          section_1_completed?: boolean | null
          section_1_summary?: string | null
          section_2_completed?: boolean | null
          section_2_overview?: string | null
          section_3_company?: string | null
          section_3_completed?: boolean | null
          section_4_completed?: boolean | null
          section_4_financial?: string | null
          section_5_completed?: boolean | null
          section_5_methodology?: string | null
          section_6_completed?: boolean | null
          section_6_results?: string | null
          section_7_completed?: boolean | null
          section_7_sensitivity?: string | null
          section_8_completed?: boolean | null
          section_8_conclusion?: string | null
          section_9_appendix?: string | null
          section_9_completed?: boolean | null
          status?: string | null
          submitted_at?: string | null
          updated_at?: string | null
          version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "tax_drafts_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      tax_reports: {
        Row: {
          created_at: string | null
          download_count: number | null
          draft_id: string | null
          file_size: number | null
          issued_at: string | null
          issued_by: string | null
          project_id: string
          report_id: string
          report_url: string
        }
        Insert: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id: string
          report_id?: string
          report_url: string
        }
        Update: {
          created_at?: string | null
          download_count?: number | null
          draft_id?: string | null
          file_size?: number | null
          issued_at?: string | null
          issued_by?: string | null
          project_id?: string
          report_id?: string
          report_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "tax_reports_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "tax_drafts"
            referencedColumns: ["draft_id"]
          },
          {
            foreignKeyName: "tax_reports_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      tax_results: {
        Row: {
          calculation_details: Json | null
          created_at: string | null
          created_by: string | null
          enterprise_value: number | null
          equity_value: number | null
          net_asset_value: number | null
          net_profit_value: number | null
          project_id: string
          result_id: string
          supplementary_value: number | null
          updated_at: string | null
          value_per_share: number | null
          weight_asset: number | null
          weight_profit: number | null
        }
        Insert: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          net_asset_value?: number | null
          net_profit_value?: number | null
          project_id: string
          result_id?: string
          supplementary_value?: number | null
          updated_at?: string | null
          value_per_share?: number | null
          weight_asset?: number | null
          weight_profit?: number | null
        }
        Update: {
          calculation_details?: Json | null
          created_at?: string | null
          created_by?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          net_asset_value?: number | null
          net_profit_value?: number | null
          project_id?: string
          result_id?: string
          supplementary_value?: number | null
          updated_at?: string | null
          value_per_share?: number | null
          weight_asset?: number | null
          weight_profit?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "tax_results_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects_legacy"
            referencedColumns: ["project_id"]
          },
        ]
      }
      tax_revisions: {
        Row: {
          assigned_to: string | null
          completed_at: string | null
          created_at: string | null
          details: string
          draft_id: string
          requested_at: string | null
          requested_by: string | null
          revision_id: string
          revision_type: string
          section: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details: string
          draft_id: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string | null
          details?: string
          draft_id?: string
          requested_at?: string | null
          requested_by?: string | null
          revision_id?: string
          revision_type?: string
          section?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "tax_revisions_draft_id_fkey"
            columns: ["draft_id"]
            isOneToOne: false
            referencedRelation: "tax_drafts"
            referencedColumns: ["draft_id"]
          },
        ]
      }
      test_valuation_results: {
        Row: {
          company_id: string
          company_name: string
          created_at: string | null
          details: Json | null
          draft_sections: Json | null
          duration_ms: number | null
          enterprise_value: number | null
          equity_value: number | null
          industry: string | null
          method: string
          result_id: string
          share_price: number | null
          situation: string | null
        }
        Insert: {
          company_id: string
          company_name: string
          created_at?: string | null
          details?: Json | null
          draft_sections?: Json | null
          duration_ms?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          industry?: string | null
          method: string
          result_id?: string
          share_price?: number | null
          situation?: string | null
        }
        Update: {
          company_id?: string
          company_name?: string
          created_at?: string | null
          details?: Json | null
          draft_sections?: Json | null
          duration_ms?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          industry?: string | null
          method?: string
          result_id?: string
          share_price?: number | null
          situation?: string | null
        }
        Relationships: []
      }
      users: {
        Row: {
          avatar_url: string | null
          company_name: string | null
          created_at: string | null
          email: string
          is_active: boolean | null
          name: string
          phone: string | null
          position: string | null
          role: string
          updated_at: string | null
          user_id: string
        }
        Insert: {
          avatar_url?: string | null
          company_name?: string | null
          created_at?: string | null
          email: string
          is_active?: boolean | null
          name: string
          phone?: string | null
          position?: string | null
          role?: string
          updated_at?: string | null
          user_id?: string
        }
        Update: {
          avatar_url?: string | null
          company_name?: string | null
          created_at?: string | null
          email?: string
          is_active?: boolean | null
          name?: string
          phone?: string | null
          position?: string | null
          role?: string
          updated_at?: string | null
          user_id?: string
        }
        Relationships: []
      }
      valuation_projects: {
        Row: {
          created_at: string | null
          current_step: number
          owner_id: string
          progress: number | null
          project_id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          current_step?: number
          owner_id: string
          progress?: number | null
          project_id: string
          status?: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          current_step?: number
          owner_id?: string
          progress?: number | null
          project_id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "valuation_projects_owner_id_fkey"
            columns: ["owner_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
      valuation_reports: {
        Row: {
          appendix: string | null
          ceo_name: string | null
          company_analysis: string | null
          company_name: string
          company_name_en: string | null
          conclusion: string | null
          created_at: string | null
          employee_count: string | null
          evaluation_overview: string | null
          evaluator: string | null
          executive_summary: string | null
          financial_summary: string | null
          founded_year: string | null
          id: number
          industry: string | null
          key_metrics: Json | null
          location: string | null
          methodology: string | null
          pdf_url: string | null
          report_url: string | null
          sensitivity_analysis: string | null
          tags: string[] | null
          updated_at: string | null
          valuation_amount_display: string | null
          valuation_amount_krw: number | null
          valuation_date: string | null
          valuation_method: string
          valuation_results: string | null
        }
        Insert: {
          appendix?: string | null
          ceo_name?: string | null
          company_analysis?: string | null
          company_name: string
          company_name_en?: string | null
          conclusion?: string | null
          created_at?: string | null
          employee_count?: string | null
          evaluation_overview?: string | null
          evaluator?: string | null
          executive_summary?: string | null
          financial_summary?: string | null
          founded_year?: string | null
          id?: number
          industry?: string | null
          key_metrics?: Json | null
          location?: string | null
          methodology?: string | null
          pdf_url?: string | null
          report_url?: string | null
          sensitivity_analysis?: string | null
          tags?: string[] | null
          updated_at?: string | null
          valuation_amount_display?: string | null
          valuation_amount_krw?: number | null
          valuation_date?: string | null
          valuation_method: string
          valuation_results?: string | null
        }
        Update: {
          appendix?: string | null
          ceo_name?: string | null
          company_analysis?: string | null
          company_name?: string
          company_name_en?: string | null
          conclusion?: string | null
          created_at?: string | null
          employee_count?: string | null
          evaluation_overview?: string | null
          evaluator?: string | null
          executive_summary?: string | null
          financial_summary?: string | null
          founded_year?: string | null
          id?: number
          industry?: string | null
          key_metrics?: Json | null
          location?: string | null
          methodology?: string | null
          pdf_url?: string | null
          report_url?: string | null
          sensitivity_analysis?: string | null
          tags?: string[] | null
          updated_at?: string | null
          valuation_amount_display?: string | null
          valuation_amount_krw?: number | null
          valuation_date?: string | null
          valuation_method?: string
          valuation_results?: string | null
        }
        Relationships: []
      }
      valuation_results: {
        Row: {
          asset_value_per_share: number | null
          asset_weight: number | null
          average_multiples: Json | null
          calc_method: string | null
          capitalization_rate: number | null
          company_name: string
          company_type: string | null
          comparable_companies: Json | null
          created_at: string | null
          current_assets: Json | null
          current_liabilities: Json | null
          discount_rate: number | null
          discounted_value_per_share: number | null
          enterprise_value: number | null
          equity_value: number | null
          fcff_projections: Json | null
          final_value_per_share: number | null
          income_3years: Json | null
          income_value: number | null
          income_weight: number | null
          industry: string | null
          interest_bearing_debt: number | null
          intrinsic_value_per_share: number | null
          liquidity_discount: number | null
          nav_discount_rate: number | null
          nav_value: number | null
          navps_adjusted: number | null
          navps_original: number | null
          net_assets: number | null
          non_current_assets: Json | null
          non_current_liabilities: Json | null
          non_operating_assets: number | null
          operating_value: number | null
          per_share_asset_value: number | null
          per_share_income_value: number | null
          per_share_values: Json | null
          profit_value_per_share: number | null
          profit_weight: number | null
          project_id: string
          pv_fcff_sum: number | null
          pv_terminal_value: number | null
          result_id: string
          sensitivity_analysis: Json | null
          shares_outstanding: number | null
          target_financials: Json | null
          terminal_growth_rate: number | null
          terminal_value: number | null
          total_assets: number | null
          total_liabilities: number | null
          totals: Json | null
          updated_at: string | null
          valuation_date: string
          valuation_method: string
          value_per_share: number | null
          wacc_components: Json | null
          weighted_avg_profit: number | null
          weighted_market_cap: number | null
          weights: Json | null
          yearly_profits: Json | null
        }
        Insert: {
          asset_value_per_share?: number | null
          asset_weight?: number | null
          average_multiples?: Json | null
          calc_method?: string | null
          capitalization_rate?: number | null
          company_name: string
          company_type?: string | null
          comparable_companies?: Json | null
          created_at?: string | null
          current_assets?: Json | null
          current_liabilities?: Json | null
          discount_rate?: number | null
          discounted_value_per_share?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          fcff_projections?: Json | null
          final_value_per_share?: number | null
          income_3years?: Json | null
          income_value?: number | null
          income_weight?: number | null
          industry?: string | null
          interest_bearing_debt?: number | null
          intrinsic_value_per_share?: number | null
          liquidity_discount?: number | null
          nav_discount_rate?: number | null
          nav_value?: number | null
          navps_adjusted?: number | null
          navps_original?: number | null
          net_assets?: number | null
          non_current_assets?: Json | null
          non_current_liabilities?: Json | null
          non_operating_assets?: number | null
          operating_value?: number | null
          per_share_asset_value?: number | null
          per_share_income_value?: number | null
          per_share_values?: Json | null
          profit_value_per_share?: number | null
          profit_weight?: number | null
          project_id: string
          pv_fcff_sum?: number | null
          pv_terminal_value?: number | null
          result_id?: string
          sensitivity_analysis?: Json | null
          shares_outstanding?: number | null
          target_financials?: Json | null
          terminal_growth_rate?: number | null
          terminal_value?: number | null
          total_assets?: number | null
          total_liabilities?: number | null
          totals?: Json | null
          updated_at?: string | null
          valuation_date: string
          valuation_method: string
          value_per_share?: number | null
          wacc_components?: Json | null
          weighted_avg_profit?: number | null
          weighted_market_cap?: number | null
          weights?: Json | null
          yearly_profits?: Json | null
        }
        Update: {
          asset_value_per_share?: number | null
          asset_weight?: number | null
          average_multiples?: Json | null
          calc_method?: string | null
          capitalization_rate?: number | null
          company_name?: string
          company_type?: string | null
          comparable_companies?: Json | null
          created_at?: string | null
          current_assets?: Json | null
          current_liabilities?: Json | null
          discount_rate?: number | null
          discounted_value_per_share?: number | null
          enterprise_value?: number | null
          equity_value?: number | null
          fcff_projections?: Json | null
          final_value_per_share?: number | null
          income_3years?: Json | null
          income_value?: number | null
          income_weight?: number | null
          industry?: string | null
          interest_bearing_debt?: number | null
          intrinsic_value_per_share?: number | null
          liquidity_discount?: number | null
          nav_discount_rate?: number | null
          nav_value?: number | null
          navps_adjusted?: number | null
          navps_original?: number | null
          net_assets?: number | null
          non_current_assets?: Json | null
          non_current_liabilities?: Json | null
          non_operating_assets?: number | null
          operating_value?: number | null
          per_share_asset_value?: number | null
          per_share_income_value?: number | null
          per_share_values?: Json | null
          profit_value_per_share?: number | null
          profit_weight?: number | null
          project_id?: string
          pv_fcff_sum?: number | null
          pv_terminal_value?: number | null
          result_id?: string
          sensitivity_analysis?: Json | null
          shares_outstanding?: number | null
          target_financials?: Json | null
          terminal_growth_rate?: number | null
          terminal_value?: number | null
          total_assets?: number | null
          total_liabilities?: number | null
          totals?: Json | null
          updated_at?: string | null
          valuation_date?: string
          valuation_method?: string
          value_per_share?: number | null
          wacc_components?: Json | null
          weighted_avg_profit?: number | null
          weighted_market_cap?: number | null
          weights?: Json | null
          yearly_profits?: Json | null
        }
        Relationships: []
      }
      valuation_results_legacy: {
        Row: {
          calculation_details: Json | null
          created_at: string | null
          enterprise_value: number | null
          equity_value: number | null
          method: string
          project_id: string | null
          result_id: number
          value_per_share: number | null
        }
        Insert: {
          calculation_details?: Json | null
          created_at?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          method: string
          project_id?: string | null
          result_id?: number
          value_per_share?: number | null
        }
        Update: {
          calculation_details?: Json | null
          created_at?: string | null
          enterprise_value?: number | null
          equity_value?: number | null
          method?: string
          project_id?: string | null
          result_id?: number
          value_per_share?: number | null
        }
        Relationships: []
      }
      weekly_collections: {
        Row: {
          collection_date: string | null
          completed_at: string | null
          created_at: string | null
          emails_generated: number | null
          error_log: string | null
          id: number
          new_companies_found: number | null
          started_at: string | null
          status: string | null
          total_news_collected: number | null
          week_number: number | null
          year: number | null
        }
        Insert: {
          collection_date?: string | null
          completed_at?: string | null
          created_at?: string | null
          emails_generated?: number | null
          error_log?: string | null
          id?: number
          new_companies_found?: number | null
          started_at?: string | null
          status?: string | null
          total_news_collected?: number | null
          week_number?: number | null
          year?: number | null
        }
        Update: {
          collection_date?: string | null
          completed_at?: string | null
          created_at?: string | null
          emails_generated?: number | null
          error_log?: string | null
          id?: number
          new_companies_found?: number | null
          started_at?: string | null
          status?: string | null
          total_news_collected?: number | null
          week_number?: number | null
          year?: number | null
        }
        Relationships: []
      }
      workflow_approvals: {
        Row: {
          approved_by: string | null
          created_at: string | null
          id: string
          project_id: string
          rationale: string | null
          status: string
          step_number: number
          updated_at: string | null
        }
        Insert: {
          approved_by?: string | null
          created_at?: string | null
          id?: string
          project_id: string
          rationale?: string | null
          status?: string
          step_number: number
          updated_at?: string | null
        }
        Update: {
          approved_by?: string | null
          created_at?: string | null
          id?: string
          project_id?: string
          rationale?: string | null
          status?: string
          step_number?: number
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "workflow_approvals_approved_by_fkey"
            columns: ["approved_by"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["user_id"]
          },
        ]
      }
    }
    Views: {
      v_latest_ranking: {
        Row: {
          last_updated: string | null
          news_count: number | null
          period_end: string | null
          period_start: string | null
          rank: number | null
          site_name: string | null
          site_number: number | null
          site_url: string | null
        }
        Insert: {
          last_updated?: string | null
          news_count?: number | null
          period_end?: string | null
          period_start?: string | null
          rank?: number | null
          site_name?: string | null
          site_number?: number | null
          site_url?: string | null
        }
        Update: {
          last_updated?: string | null
          news_count?: number | null
          period_end?: string | null
          period_start?: string | null
          rank?: number | null
          site_name?: string | null
          site_number?: number | null
          site_url?: string | null
        }
        Relationships: []
      }
    }
    Functions: {
      update_news_ranking: { Args: never; Returns: undefined }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const
