# AI Agent SaaS Platform - Architecture Overview

## 1. Vision
A multi-tenant SaaS platform that enables enterprises to build and manage AI-powered digital twin agents for their executives across Microsoft Teams. The solution combines a clean architecture ASP.NET Core backend, an Angular 17 front-end, PostgreSQL storage, and deep integration with Microsoft 365 and Stripe.

## 2. High-Level Architecture
```
+--------------------+         +-----------------------+
| Angular Front-end  | <-----> | ASP.NET Core 8 Web API|
+--------------------+  HTTPS  +-----------------------+
          |                             |
          v                             v
   Microsoft Identity          PostgreSQL (via EF Core)
          |                             |
          v                             v
    Microsoft Graph API        Stripe API & Webhooks
```

The solution is organized using Clean Architecture principles with independent Core, Application, Infrastructure, and API layers to ensure maintainability, testability, and scalability.

## 3. Solution Structure
```
/ai-agent-saas
├── backend
│   ├── src
│   │   ├── AIWorks.Core
│   │   ├── AIWorks.Application
│   │   ├── AIWorks.Infrastructure
│   │   └── AIWorks.Api
│   ├── tests
│   │   ├── AIWorks.UnitTests
│   │   └── AIWorks.IntegrationTests
│   └── AIWorks.sln
└── frontend
    ├── aiworks-portal
    └── package.json
```

### Layer Responsibilities
- **Core**: Domain entities, value objects, enums, interfaces, and business rules. Pure C# without dependencies.
- **Application**: Use cases, CQRS handlers (MediatR), DTOs, validators (FluentValidation), and abstractions for services.
- **Infrastructure**: EF Core DbContext, repository implementations, external service clients (Microsoft Graph, Stripe), configuration, and persistence migrations.
- **API**: ASP.NET Core Web API project exposing REST endpoints, authentication/authorization, controllers, minimal API endpoints, Swagger, and dependency injection configuration.

## 4. Key Technologies
- ASP.NET Core 8 Web API
- Entity Framework Core with Npgsql provider
- MediatR for CQRS
- FluentValidation
- Microsoft.Identity.Web & Azure AD
- MSAL.js for SPA authentication
- Angular 17 standalone components
- Tailwind CSS + Angular Material
- Stripe .NET SDK and Stripe.js
- Serilog for structured logging
- xUnit + FluentAssertions + Respawn for tests

## 5. Database Schema
Entity definitions for Tenant, User, Agent, Interaction, MicrosoftConnection, Subscription following the schema provided in the requirements. Soft deletes via shadow properties and global query filters enforce tenant isolation.

### Multi-Tenancy Strategy
- Tenant context resolved per-request through JWT claims (TenantId) and persisted in the Application layer.
- DbContext applies a global filter `builder.HasQueryFilter(e => e.TenantId == _currentTenant.Id)`.
- Migrations stored in `AIWorks.Infrastructure/Migrations` and executed via `dotnet ef database update`.

## 6. Authentication & Authorization Flow
1. Angular app uses MSAL.js to initiate Azure AD login (single-tenant or multi-tenant depending on configuration).
2. Upon successful authentication, the front-end requests an API token by calling `/api/auth/microsoft/login` with the Azure AD ID token.
3. The API validates the token with Microsoft.Identity.Web, provisions or updates the user/tenant records, and issues a JWT containing TenantId, Role, and permissions claims.
4. API endpoints require bearer JWT tokens and enforce policies via ASP.NET Core authorization handlers.
5. Refresh tokens handled via secure HTTP-only cookies; access tokens stored in encrypted column using `IDataProtectionProvider`.

## 7. Onboarding Workflow
- Angular wizard guiding company registration, Microsoft 365 connection, and trial activation.
- Backend orchestrates tenant creation, Microsoft Graph consent tracking, and seed data for Free tier usage quotas.
- Background hosted service polls Graph API status updates during agent learning.

## 8. Agent Lifecycle
1. **Creation**: Wizard selects target executive from Graph API, configures channels, and triggers `CreateAgentCommand`.
2. **Learning**: Background job (Hangfire or Azure Functions) ingests communication metadata and builds personality profile stored as JSON.
3. **Activation**: Agent transitions to Active status once training completes and is available for Teams chat/meeting integrations (future hooks).
4. **Analytics**: Daily job aggregates interactions into reporting tables, exposed through `/api/agents/{id}/analytics` endpoints.

## 9. Billing & Subscription
- Stripe Checkout integration via `/api/subscriptions/checkout` endpoint.
- Webhook endpoint validates signatures and updates tenant subscription state.
- Customer portal URL generated for self-service management.
- Usage tracking stored per tenant and enforced via middleware to block overages.

## 10. Front-end Highlights
- Angular 17 app with standalone components, router-based layout, and lazy-loaded feature modules (Dashboard, Agents, Billing, Settings).
- Tailwind utility classes for layout plus Angular Material components for inputs, tables, and charts (using ngx-charts or Chart.js).
- State management with NgRx or Angular signals store for authentication and tenant context.
- Responsive design supporting desktop, tablet, and mobile breakpoints.

## 11. DevOps & Deployment
- GitHub Actions pipeline for CI/CD (build, test, lint).
- Infrastructure as Code via Bicep/Terraform to provision Azure App Service, Azure PostgreSQL, Key Vault, and Azure Storage for logs.
- Production monitoring with Application Insights.

## 12. Next Steps
1. Initialize Git submodules/projects for backend and frontend scaffolding.
2. Configure Azure AD app registrations and environment variables.
3. Implement authentication endpoints and Angular MSAL integration.
4. Build onboarding wizard and dashboard stub with mock data.
5. Implement Stripe integration and webhook handling.
6. Gradually enhance agent management and analytics features.

This document serves as the foundation for implementing the production-ready AI Agent SaaS platform and can be extended with more detailed sequence diagrams, API contracts, and UI wireframes as the project evolves.
