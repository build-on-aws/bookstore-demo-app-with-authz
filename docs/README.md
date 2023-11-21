# Introduction to authorization scenarios with Amazon Verified Permissions

In our bookstore application, you will see integrated a non-trivial authorization system using Amazon Verified Permissions (AVP). This system enhances our application's security and flexibility by managing user access to various resources and features.

## Overview of Amazon Verified Permissions Integration

Amazon Verified Permissions operates on a default "deny all" basis. This means that unless a policy explicitly allows an action, it is denied by default. This approach ensures maximum security, as access is restricted unless specifically granted.

AVP provides a robust framework for defining and enforcing access control policies. Key components of our integration include:

### Policy Store

- **Description:** The Policy Store in AVP acts as a repository for our access control policies. It contains both 'allow' and 'deny' policies, which define the rules for user access based on their roles and attributes.

### Authorization Decision

- **Description:** Before any data is returned from our database, an authorization request is made to AVP. This request evaluates the user's information against the policies in the Policy Store to make an authorization decision. This ensures that users only access data and features they are permitted to.

## Understanding the Authorization Schema in Amazon Verified Permissions

The authorization schema in Amazon Verified Permissions (AVP) defines the structure and rules for authorization requests within our bookstore application. It outlines the entities, actions, and contexts that are considered when making authorization decisions. Let's break down the key components of this schema:

### Schema Overview

```json
{
    "Bookstore": {
        "actions": {
            "View": { ... },
            "ViewPremiumOffers": { ... }
        },
        "entityTypes": {
            "User": { ... },
            "Role": { ... },
            "Book": { ... }
        }
    }
}
```

## Actions

- **View**: This action allows users to view books. It applies to the 'Book' resource type and requires a 'region' context attribute.
- **ViewPremiumOffers**: Similar to 'View', but specifically for viewing premium offers. It also requires a 'region' context attribute.

## Entity Types

- **User**: Represents an individual user. It includes an optional attribute 'yearsAsMember' to track the duration of membership.
- **Role**: Defines different roles within the system, like 'Admin', 'Customer', or 'Publisher'.
- **Book**: Represents a book entity. It includes an 'owner' attribute, linking to a 'User' entity.

### Users

To execute all prepared scenarios, please create a following set of users:

| User Name | Role      | Years as Member | Password                   | Email                 |
| --------- | --------- | --------------- |----------------------------|-----------------------|
| Tom       | Admin     | Any value       | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |
| Frank     | Admin     | Any value       | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |
| Dante     | Publisher | Any value       | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |
| Andrew    | Customer  | 3               | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |
| Susan     | Customer  | 1               | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |
| Toby      | Customer  | Any value       | <PUT_HERE_A_SAFE_PASSWORD> | <PUT_HERE_REAL_EMAIL> |

Keep in mind to use a valid email address for each user, as they need to provide a verification code that will be sent after signing up by *Amazon Cognito*.

### Roles

- **Admin**: People that have administrative privileges. _TL;DR_: they can see _EVERYTHING_.
- **Publisher**: People that can list books which they were published by them.
- **Customer**: People that can list the books depending on how long they are customers of our bookstore (loyal customer will have access to premium offers).

## Context

- **Region**: A required attribute in the context of both 'View' and 'ViewPremiumOffers' actions. It ensures that the user's region is considered during authorization, which can be crucial for region-specific access control.

## Purpose of the Schema

- **Structure and Validation**: The schema defines the structure of authorization requests and validates them against the defined entities and actions.
- **Flexibility and Control**: It allows for flexible and fine-grained control over who can perform what actions on which resources, under what conditions.
- **Contextual Decisions**: The inclusion of context like 'region' enables more nuanced authorization decisions based on additional information beyond just user roles and permissions.

## Why Context Matters

- **Enhanced Security**: Context attributes like 'region' can be used to restrict access based on geographical location, enhancing security and compliance.
- **Customized Access Control**: It allows for more tailored access control decisions, taking into account specific aspects of the user's environment or situation.

In summary, the authorization schema in AVP is a critical component that defines the rules and structure for making authorization decisions in our bookstore application. It ensures that each authorization request is evaluated comprehensively, considering the user's role, the action they wish to perform, the resource in question, and relevant contextual information.

## Scenarios

We have crafted several scenarios to demonstrate the capabilities of our authorization system. These scenarios cover a range of user roles and actions, showcasing how AVP dynamically allows or denies access based on user attributes and defined policies. The scenarios include:

- **Admin Access:** Demonstrating complete access for administrative users.
- **Publisher Restrictions:** Managing access for publishers to only their published books.
- **Customer Access:** Tailoring content visibility for customers, including premium offers based on membership duration.
- **Explicit Permissions:** Granting specific users access to particular resources.
- **Contextual Restrictions:** Implementing access control based on contextual information like user location.

### Scenario 1: RBAC - Admin Access

#### User Requirement

- **User Name:** Tom
- **Cognito Attributes:**
  - **Role:** Admin
  - **Years as Member:** Not applicable for this role, so could be any value.
  - **Location:** United States (USA)

#### Relevant AVP Policy

- **Policy Name:** `RbacAdminStaticPolicy` (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  permit(
    principal in Bookstore::Role::"Admin",
    action in [Bookstore::Action::"View"],
    resource
  );
  ```
- **Description:** This policy allows users with the role of 'Admin' to view all books in the bookstore. It is an 'allow' policy that grants complete access to the book inventory.

#### Expected Data Visibility

- **Outcome:** The AdminUser will have access to view all books in the bookstore, including regular and premium offers.
- **Rationale:** Since the Admin role is granted full access to view all books through the RbacAdminStaticPolicy, the AdminUser will see the complete list of books without any restrictions.

### Understanding the Authorization Request for Admin User 'Tom'

The authorization request for the user 'Tom' with the role 'Admin' is structured to determine his access rights within the bookstore application. Here's a breakdown of the request:

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Tom"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "View"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Tom"
        },
        "attributes": {},
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Admin"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "US"
      }
    }
  }
}
```

Tom is associated with the 'Admin' role. This role is crucial in determining his access rights (RBAC)

### Scenario 2: Explicit Deny for Admin User 'Frank' (RBAC)

#### User Requirement

- **User Name:** Frank
- **Cognito Attributes:**
  - **Role:** Admin
  - **Years as Member:** Not applicable for this role, so could be any value.
  - **Location:** United States (USA)

#### Relevant AVP Policy

- **Policy Name:** `ExplicitDenyAdminFrankPolicy` (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  forbid(
    principal == Bookstore::User::"Frank",
    action in [Bookstore::Action::"View"],
    resource
  );
  ```
- **Description:** This policy allows users with the role of 'Admin' to view all books in the bookstore. It is an 'allow' policy that grants complete access to the book inventory.

#### Expected Data Visibility

- **Outcome:** Admin User Frank will be denied access to view any books in the bookstore.
- **Rationale:** Despite having an Admin role, the ExplicitDenyAdminFrankPolicy specifically denies Frank from viewing books. This scenario demonstrates the precedence of explicit deny policies over allow policies in access control.

### Understanding the Authorization Request for Admin User 'Frank'

The authorization request for the user 'Frank' with the role 'Admin' is structured to determine his access rights within the bookstore application. Here's a breakdown of the request:

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE_ID",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Frank"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "View"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Frank"
        },
        "attributes": {},
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Admin"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "US"
      }
    }
  }
}
```

In this scenario, the explicit deny policy for Frank takes precedence, showcasing the power and flexibility of fine-grained access control in AVP. Despite his Admin role, Frank's access to view books is explicitly denied, illustrating the importance of specific policy definitions in access management.

### Scenario 3: Publisher Resource Owner - User Dante: Bulk Authorization

#### User Requirement

- **User Name:** Dante
- **Cognito Attributes:**
  - **Role:** Publisher
  - **Years as Member:** Not applicable for this role, so could be any value.
  - **Location:** United States (USA)

#### Relevant AVP Policies

1. **Policy Name:** `RbacResourceOwnerStaticPolicy` (in `authorization.yaml` file)
   **Definition:**
   ```cedar
   permit (
     principal in Bookstore::Role::"Publisher",
     action in [ Bookstore::Action::"View" ],
     resource
   )
   when {
     principal == resource.owner
   };
   ```
   **Description:** Allows any user with the role of Publisher (like Dante), to view the books he has published. This policy is based on the role of the user as a Publisher and the ownership of the book, ensuring that publishers can access their own published works.
2. **Policy Name:** `RbacExplicitStaticPolicy` (in `authorization.yaml` file)
   **Definition:**
   ```cedar
   permit(
     principal == Bookstore::User::"Dante",
     action in [ Bookstore::Action::"View" ],
     resource == Bookstore::Book::"em1oadaa-b22k-4ea8-kk33-f6m217604o3m"
   );
   ```
   **Description:** This policy allows the user with the specific identifier (Dante) to view the book with the identifier `em1oadaa-b22k-4ea8-kk33-f6m217604o3m`. It's an explicit 'allow' policy that grants access to a particular resource in the database.

#### Expected Data Visibility

- **Outcome:** Publisher Dante will have access to view the specific books that he has published, as well as the book explicitly specified in the second policy.
- **Rationale:** The combined policies grant Dante, as a publisher, the right to view his own published books and a specific book identified by its unique resource identifier. This scenario demonstrates role-based access control combined with resource ownership and explicit resource identification.

### Bulk Authorization for Publisher User 'Dante'

In this scenario, we implement bulk authorization to efficiently handle multiple authorization requests for Dante. Bulk authorization allows us to process several authorization checks in a single request, enhancing performance and scalability.

#### What is Bulk Authorization?

Bulk authorization is a method of processing multiple authorization requests simultaneously. Instead of sending individual requests for each resource, a batch request is sent containing multiple entities and resources. This approach is particularly useful for users like publishers who need access to a large number of resources.

#### Benefits of Bulk Authorization

- **Efficiency:** Reduces the number of individual authorization requests, making the process faster.
- **Scalability:** Handles multiple requests in one operation, ideal for scenarios with numerous resources.
- **Improved User Experience:** Provides quicker and more streamlined access to multiple resources.

#### Bulk Authorization Request for Dante

```json
{
  "policyStoreId": "YOUR_POLICY_STORE",
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Dante"
        },
        "attributes": {},
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Publisher"
          }
        ]
      },
      {
        "identifier": {
          "entityType": "Bookstore::Book",
          "entityId": "em1oadaa-b22k-4ea8-kk33-f6m217604o3m"
        },
        "attributes": {
          "owner": {
            "entityIdentifier": {
              "entityType": "Bookstore::User",
              "entityId": "William"
            }
          }
        },
        "parents": []
      },
      {
        "identifier": {
          "entityType": "Bookstore::Book",
          "entityId": "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
        },
        "attributes": {
          "owner": {
            "entityIdentifier": {
              "entityType": "Bookstore::User",
              "entityId": "Dante"
            }
          }
        },
        "parents": []
      }
    ]
  },
  "requests": [
    {
      "principal": {
        "entityType": "Bookstore::User",
        "entityId": "Dante"
      },
      "action": {
        "actionType": "Bookstore::Action",
        "actionId": "View"
      },
      "resource": {
        "entityType": "Bookstore::Book",
        "entityId": "em1oadaa-b22k-4ea8-kk33-f6m217604o3m"
      },
      "context": {
        "contextMap": {
          "region": {
            "string": "US"
          }
        }
      }
    },
    {
      "principal": {
        "entityType": "Bookstore::User",
        "entityId": "Dante"
      },
      "action": {
        "actionType": "Bookstore::Action",
        "actionId": "View"
      },
      "resource": {
        "entityType": "Bookstore::Book",
        "entityId": "fn2padaa-c33l-4ea8-ll44-g7n217604p4n"
      },
      "context": {
        "contextMap": {
          "region": {
            "string": "US"
          }
        }
      }
    }
  ]
}
```

### Scenario 4: ABAC - Loyal Customer Access to Premium Offers Part I

#### User Requirement

- **User Name:** Andrew
- **Cognito Attributes:**
  - **Role:** Customer
  - **Years as Member:** 3
  - **Location:** United States (USA)

#### Relevant AVP Policy

- **Policy Name:** `PermitAbacStaticPolicy` (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  permit (
    principal in Bookstore::Role::"Customer",
    action in [Bookstore::Action::"ViewPremiumOffers"],
    resource
  )
  when {
    principal has yearsAsMember && principal.yearsAsMember >= 2
  };
  ```
- **Description:** This policy allows customers who have been members for 2 or more years to view premium offers on books. It leverages the `yearsAsMember` attribute for Attribute-Based Access Control (ABAC).

#### Expected Data Visibility

- **Outcome:** Andrew, as a loyal customer with 3 years of membership, will have access to view both regular books and books with premium offers.
- **Rationale:** The policy specifically targets customers with a membership duration of 2 or more years, granting them additional privileges to view premium offers. Andrew's membership duration of 3 years qualifies him for this access.

### Understanding the Authorization Request for Customer 'Andrew'

The authorization request for Andrew is designed to evaluate his eligibility for viewing premium offers based on his membership duration.

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Andrew"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "ViewPremiumOffers"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Andrew"
        },
        "attributes": {
          "yearsAsMember": {
            "long": 3
          }
        },
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Customer"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "US"
      }
    }
  }
}
```

In this scenario, Andrew's role as a 'Customer' and his 'yearsAsMember' attribute are key factors in determining his access rights. The ABAC approach allows for a more dynamic and flexible access control mechanism, adapting to the attributes of individual users.

### ### Scenario 4: ABAC - Loyal Customer Access to Premium Offers Part I

#### User Requirement

- **User Name:** Andrew
- **Cognito Attributes:**
  - **Role:** Customer
  - **Years as Member:** 3
  - **Location:** United States (USA)

#### Relevant AVP Policy

- **Policy Name:** `PermitAbacStaticPolicy` (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  permit (
    principal in Bookstore::Role::"Customer",
    action in [Bookstore::Action::"ViewPremiumOffers"],
    resource
  )
  when {
    principal has yearsAsMember && principal.yearsAsMember >= 2
  };
  ```
- **Description:** This policy allows customers who have been members for 2 or more years to view premium offers on books. It leverages the `yearsAsMember` attribute for Attribute-Based Access Control (ABAC).

#### Expected Data Visibility

- **Outcome:** Andrew, as a loyal customer with 3 years of membership, will have access to view both regular books and books with premium offers.
- **Rationale:** The policy specifically targets customers with a membership duration of 2 or more years, granting them additional privileges to view premium offers. Andrew's membership duration of 3 years qualifies him for this access.

### Understanding the Authorization Request for Customer 'Andrew'

The authorization request for Andrew is designed to evaluate his eligibility for viewing premium offers based on his membership duration.

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Andrew"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "ViewPremiumOffers"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Andrew"
        },
        "attributes": {
          "yearsAsMember": {
            "long": 3
          }
        },
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Customer"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "US"
      }
    }
  }
}
```

In this scenario, Andrew's role as a 'Customer' and his 'yearsAsMember' attribute are key factors in determining his access rights. The ABAC approach allows for a more dynamic and flexible access control mechanism, adapting to the attributes of individual users.

## Scenario 4: ABAC - Loyal Customer Access to Premium Offers (Part II)

#### User Requirement

- **User Name:** Susan
- **Cognito Attributes:**
  - **Role:** Customer
  - **Years as Member:** 1
  - **Location:** United States (USA)

#### Relevant AVP Policy

- **Policy Name:** DenyAbacStaticPolicy (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  forbid(
    principal in Bookstore::Role::"Customer",
    action in [Bookstore::Action::"ViewPremiumOffers"],
    resource
  )
  when {
    principal has yearsAsMember && principal.yearsAsMember < 2
  };
  ```
- **Description:** This policy denies customers who have been members for less than 2 years the ability to view premium offers on books. It uses the `yearsAsMember` attribute for Attribute-Based Access Control (ABAC).

#### Expected Data Visibility

- **Outcome:** Susan, as a new customer with only 1 year of membership, will not have access to view premium offers on books. However, she can still view regular books and offers.
- **Rationale:** The policy is designed to restrict access to premium offers for customers with less than 2 years of membership. Susan's membership duration of 1 year falls below this threshold, hence denying her access to premium offers.

### Understanding the Authorization Request for Customer 'Susan'

The authorization request for Susan assesses her eligibility for viewing premium offers based on her membership duration.

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE_ID",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Susan"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "ViewPremiumOffers"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Susan"
        },
        "attributes": {
          "yearsAsMember": {
            "long": 1
          }
        },
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Customer"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "US"
      }
    }
  }
}
```

In this scenario, Susan's role as a 'Customer' and her 'yearsAsMember' attribute are crucial in determining her access rights. The ABAC approach allows for nuanced access control, where attributes like membership duration directly influence the level of access granted to users.

### Scenario 5: Context-Based Access Control - Regional Restriction

#### User Requirement

- **User Name:** Toby
- **Cognito Attributes:**
  - **Role:** Customer
  - **Years as Member:** Not important for this scenario
  - **Location:** United Kingdom (UK)

#### Relevant AVP Policy

- **Policy Name:** `ContextStaticPolicy` (in `authorization.yaml` file)
- **Definition:**
  ```cedar
  forbid(
    principal,
    action in [Bookstore::Action::"View", Bookstore::Action::"ViewPremiumOffers"],
    resource
  )
  when {
    context.region != "US"
  };
  ```
- **Description:** This policy denies access to viewing books and premium offers for users located outside the United States. It utilizes the region context attribute, which is derived from the user's IP address, to enforce regional access restrictions.

#### Expected Data Visibility

- **Outcome:** Toby, being located in the UK, will be denied access to view both regular and premium book offers in the bookstore.
- **Rationale:** The policy explicitly restricts access to users outside the US. Since Toby's location is identified as the UK, he falls under the restriction and is thus denied access.

### Understanding the Authorization Request for User 'Toby'

The authorization request for Toby is structured to assess his access rights based on his geographical location.

#### Authorization Request Details

```json
{
  "policyStoreId": "YOUR_POLICY_STORE_ID",
  "principal": {
    "entityType": "Bookstore::User",
    "entityId": "Toby"
  },
  "action": {
    "actionType": "Bookstore::Action",
    "actionId": "ViewPremiumOffers"
  },
  "resource": {
    "entityType": "Bookstore::Book",
    "entityId": "*"
  },
  "entities": {
    "entityList": [
      {
        "identifier": {
          "entityType": "Bookstore::User",
          "entityId": "Toby"
        },
        "attributes": {
          "yearsAsMember": {
            "long": 4
          }
        },
        "parents": [
          {
            "entityType": "Bookstore::Role",
            "entityId": "Customer"
          }
        ]
      }
    ]
  },
  "context": {
    "contextMap": {
      "region": {
        "string": "UK"
      }
    }
  }
}
```

In this scenario, the region context attribute plays a pivotal role. Despite Toby's role and membership duration, his location outside the US leads to the denial of access to the bookstore's offerings. This demonstrates the power of context-based access control in enforcing location-specific policies.
