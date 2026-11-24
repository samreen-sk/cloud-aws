# CloudFile Manager – AWS S3 Cloud Storage

## 1. Project Overview

CloudFile Manager is a cloud storage mini-project built using **Amazon S3 (Simple Storage Service)**.

The objective of this project is to understand how cloud storage works and how AWS manages files, versions, access permissions, encryption and storage costs.

The project demonstrates how to:

- Store CSV and JSON files in Amazon S3.
- Organize files using S3 object keys and prefixes.
- Maintain multiple versions of uploaded files.
- Recover previous versions of files.
- Automatically transition older objects to cheaper storage classes.
- Secure storage using IAM and Bucket Policies.
- Encrypt objects using server-side encryption.
- Upload and download files using AWS CLI.

**AWS Service:** Amazon S3  
**Project Name:** CloudFile Manager  
**Bucket Type:** General Purpose  
**Region:** Asia Pacific (Mumbai) – ap-south-1 (if selected during setup)

---

## 2. Architecture

```text
          Windows Computer
                 |
                 |
          CSV and JSON Files
                 |
                 |
       AWS Management Console
                 |
                 | Upload
                 v
          Amazon S3 Bucket
                 |
       +---------+----------+
       |         |          |
     active/   archive/   backups/
       |         |          |
       +---------+----------+
                 |
          S3 Versioning
                 |
          Lifecycle Rules
                 |
       Storage Class Transition
                 |
       +---------+----------------+
       |                          |
   IAM Permissions           Encryption
       |                          |
   Bucket Policies          SSE-S3 / HTTPS
       |
   AWS CLI Operations
   (Upload / Download)
```

### How the system works

1. Files are created locally on the computer.
2. Files are uploaded to an S3 bucket.
3. S3 stores the files as objects.
4. Versioning preserves previous versions when objects are overwritten or normally deleted.
5. Lifecycle Policies automatically transition eligible objects to cheaper storage classes.
6. IAM controls which identities can perform S3 operations.
7. Bucket Policies enforce additional access restrictions.
8. SSE-S3 encrypts objects at rest.
9. AWS CLI provides command-line access to upload, download and inspect objects.

---

## 3. Understanding Amazon S3

### What is Amazon S3?

Amazon S3 is an AWS object storage service used to store and retrieve data from anywhere over the internet.

It is commonly used for:

- Application file storage.
- Images and videos.
- Database backups.
- CSV and JSON files.
- Logs and reports.
- Data lakes and archival storage.

### Important S3 Terminology

| Term | Explanation |
|---|---|
| Bucket | Container used to store objects |
| Object | Actual file stored in S3 along with its metadata |
| Object Key | Unique name identifying an object within a bucket |
| Prefix | Part of an object key used to organize objects |
| Storage Class | Determines storage characteristics and pricing |
| Version ID | Unique identifier assigned to an object version |
| Lifecycle Policy | Automatically transitions or expires objects |
| Bucket Policy | Resource-based JSON policy attached to a bucket |

**Important:** S3 does not use traditional physical folders. It stores objects using keys.

For example:

```text
active/employees.csv
```

Here:

- `active/` is the prefix.
- `employees.csv` is the object name.
- `active/employees.csv` is the complete object key.

The S3 Console displays prefixes as folders for easier organization.

---

## 4. Project Implementation

### Step 1 – Create an S3 Bucket

**Why did we create a bucket?**

We needed a central location to store our CSV and JSON files.

Implementation:

1. Open AWS Management Console.
2. Search for Amazon S3.
3. Select Create bucket.
4. Choose General Purpose bucket.
5. Provide a globally unique bucket name.
6. Select the required AWS Region.
7. Configure Object Ownership.
8. Enable Block Public Access.
9. Enable Bucket Versioning.
10. Enable default encryption using SSE-S3.
11. Keep Object Lock disabled.
12. Create the bucket.

### Bucket Configuration

| Setting | Selected Configuration |
|---|---|
| Bucket Type | General Purpose |
| Object Ownership | Bucket owner enforced |
| ACLs | Disabled |
| Block Public Access | Enabled |
| Versioning | Enabled |
| Default Encryption | SSE-S3 |
| Object Lock | Disabled |

**Why these settings?**

- Bucket owner enforced: Manages permissions through IAM and policies instead of ACLs.
- Block Public Access: Prevents accidental public access.
- Versioning: Preserves previous object versions.
- SSE-S3: Automatically encrypts objects at rest.
- Object Lock disabled: We don't require immutable object retention for this project.

### Step 2 – Create and Upload Files

We created two sample files locally.

Project structure:

```text
CloudFileManager/
    uploads/
        employees.csv
        config.json
```

**employees.csv**

```csv
id,name,department,salary
1,John,Engineering,50000
2,Alice,HR,45000
3,David,Finance,55000
```

**config.json**

```json
{
  "application": "CloudFileManager",
  "version": "1.0",
  "environment": "development",
  "storage": "Amazon S3"
}
```

We uploaded these files through the AWS Management Console.

Upload procedure:

1. Open the S3 bucket.
2. Select Upload.
3. Click Add files.
4. Select the CSV and JSON files.
5. Keep the storage class as S3 Standard.
6. Keep encryption enabled.
7. Click Upload.

**What happened?**

S3 created two objects inside the bucket.

The original files remain on our local computer. Uploading creates copies in cloud storage.

### Step 3 – Organize Objects Using Prefixes

We created the following organization:

```text
cloudfile-manager/
    active/
        employees.csv
        config.json

    archive/

    backups/
```

Purpose of each prefix:

| Prefix | Purpose |
|---|---|
| active/ | Currently used files |
| archive/ | Older files that are rarely accessed |
| backups/ | Copies retained for recovery |

**Important:** These prefixes are used for logical organization. They do not automatically determine the storage class.

For example, putting a file inside `archive/` does not automatically move it to Glacier. We need Lifecycle Policies for that.

### Step 4 – Enable and Test Versioning

**Why do we need Versioning?**

Imagine we have a configuration file:

Version 1:

```json
{
  "application": "CloudFileManager",
  "version": "1.0"
}
```

Later, we modify it:

Version 2:

```json
{
  "application": "CloudFileManager",
  "version": "2.0"
}
```

If we upload Version 2 using the same object key, S3 creates a new current version while preserving the previous version.

Without Versioning, the previous content would normally be overwritten.

**Implementation:**

1. Open the S3 bucket.
2. Go to Properties.
3. Find Bucket Versioning.
4. Verify that it is Enabled.
5. Modify the local config.json from version 1.0 to 2.0.
6. Upload the modified file into the same `active/` prefix using the same object key.
7. Open the object and select Show versions.

We should see two versions.

**Important Versioning Concepts**

| Concept | Explanation |
|---|---|
| Version ID | Unique identifier of an object version |
| Current Version | Latest version |
| Noncurrent Version | Older version |
| Delete Marker | Marker created when a versioned object is normally deleted |

**Delete Marker:**

When we normally delete a versioned object, S3 creates a delete marker.

The previous versions remain stored.

Removing the delete marker can make the previous version visible again.

Versioning helps recover accidentally overwritten or normally deleted objects. It is not a substitute for a complete backup and security strategy.

### Step 5 – Configure Lifecycle Policies

**Why do we need Lifecycle Policies?**

Imagine an application stores thousands of files.

Some files are accessed every day, while others are rarely accessed.

Keeping everything in S3 Standard may not be cost-efficient.

S3 Lifecycle Policies automate storage transitions according to predefined rules.

**Our storage strategy:**

| Object Age | Storage Class | Purpose |
|---|---|---|
| Day 0 | S3 Standard | Frequently accessed |
| Day 30 | S3 Standard-IA | Infrequently accessed |
| Day 90 | S3 Glacier Flexible Retrieval | Long-term archival |

**Configuration:**

1. Open the S3 bucket.
2. Select Management.
3. Open Lifecycle rules.
4. Click Create lifecycle rule.
5. Name it `cloudfile-storage-lifecycle`.
6. Limit the scope using a prefix filter.
7. Enter `archive/`.
8. Enable the lifecycle rule.

Select the action:

Transition current versions of objects between storage classes.

Configure:

Transition 1:

- Storage class: S3 Standard-IA
- Days after object creation: 30

Transition 2:

- Storage class: S3 Glacier Flexible Retrieval
- Days after object creation: 90

Also configure noncurrent version transitions:

- Days after becoming noncurrent: 30
- Storage class: S3 Glacier Flexible Retrieval.

We did not configure permanent deletion or expiration.

**Important Lifecycle Concepts:**

- Current version transition: Moves the current object version to another storage class.
- Noncurrent version transition: Moves older versions to another storage class.
- Lifecycle Rule: Defines when and how transitions happen.
- Prefix Filter: Limits which objects the rule applies to.

**Cost Considerations:**

- S3 Standard-IA has a 30-day minimum storage duration.
- S3 Glacier Flexible Retrieval has a 90-day minimum storage duration.
- Objects smaller than 128 KB are not transitioned by default under current lifecycle behavior.
- Retrieval and transition requests may incur charges.
- Lifecycle transitions are asynchronous and do not happen immediately.

The 30-day and 90-day current-version transition timings are measured from the object's creation date.

### Step 6 – Configure Bucket Policies

**Why do we need Bucket Policies?**

A Bucket Policy is a JSON-based resource policy attached directly to an S3 bucket.

It allows us to control access to bucket resources.

For our project, we configured an HTTPS-only policy.

**Implementation:**

1. Open the S3 bucket.
2. Select Permissions.
3. Find Bucket Policy.
4. Click Edit.
5. Replace the bucket name in the policy.
6. Save changes.

Policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::YOUR_BUCKET_NAME",
        "arn:aws:s3:::YOUR_BUCKET_NAME/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

**Understanding the policy:**

| Field | Explanation |
|---|---|
| Version | Policy language version |
| Sid | Statement identifier |
| Effect | Allow or Deny |
| Principal | Identity to which the statement applies |
| Action | AWS operation |
| Resource | Bucket and object ARN |
| Condition | Condition under which the policy applies |

`aws:SecureTransport = false` means the request is using an insecure HTTP connection.

The policy explicitly denies such requests.

It does not grant public access.

### Step 7 – Configure IAM-Based Access

**Why do we need IAM?**

Suppose an application running on EC2 needs to upload files into S3.

We should not provide unrestricted access to all AWS resources.

Instead, we use an IAM Role with a limited permission policy.

Architecture:

```text
EC2 Application
      |
      v
   IAM Role
      |
      v
   IAM Policy
      |
      v
   S3 Bucket
```

**Implementation:**

1. Open IAM.
2. Select Policies.
3. Click Create Policy.
4. Choose JSON.
5. Add the required permissions.
6. Replace the bucket name.
7. Create the policy.

Example policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

Policy name:

`CloudFileManagerS3Access`

This policy allows:

- Listing objects.
- Uploading objects.
- Downloading objects.

It does not allow deleting objects or modifying bucket configuration.

**IAM Policy vs Bucket Policy**

| IAM Policy | Bucket Policy |
|---|---|
| Identity-based policy | Resource-based policy |
| Attached to IAM users, groups or roles | Attached to an S3 bucket |
| Defines what an identity can do | Defines access to bucket resources |

For an application running on EC2, we can attach this policy to an EC2 IAM role. The instance receives temporary credentials through the role.

Our current console and CLI operations use the permissions of our IAM identity. The EC2 role is intended for future application integration.

### Step 8 – Encryption and Security

**Why encryption?**

Encryption protects stored information from being read by unauthorized parties.

We configured two security mechanisms.

**1. Encryption at Rest**

Our bucket uses SSE-S3.

SSE-S3 means Server-Side Encryption with Amazon S3 Managed Keys.

Amazon S3 manages the encryption keys and automatically encrypts stored objects.

**2. Encryption in Transit**

HTTPS/TLS protects information while it travels between our computer and AWS.

Our HTTPS-only Bucket Policy helps enforce secure transport.

**Different Encryption Types**

| Encryption | Key Management |
|---|---|
| SSE-S3 | Amazon S3 manages keys |
| SSE-KMS | AWS KMS manages keys |
| SSE-C | Customer provides encryption keys |

For this project, we selected SSE-S3 because it is simple and sufficient for our learning requirements.

---

## 5. AWS CLI – Upload and Download Files

AWS CLI allows us to interact with AWS services using commands instead of the AWS Console.

**Why do we need AWS CLI?**

Imagine uploading hundreds of files every day.

Uploading files individually through the console is inconvenient.

CLI allows us to automate file operations.

### Step 1 – Verify AWS CLI Installation

```powershell
aws --version
```

### Step 2 – Authenticate

For an IAM Identity Center profile:

```powershell
aws configure sso
```

Complete the prompts for:

- SSO Start URL
- SSO Region
- AWS Account
- Permission Set
- Profile Name

We use the profile name:

`cloud-admin`

Login:

```powershell
aws sso login --profile cloud-admin
```

Verify identity:

```powershell
aws sts get-caller-identity --profile cloud-admin
```

This returns the account ID, ARN and user ID of the authenticated identity.

If using IAM user access keys instead, configure a named profile using `aws configure --profile cloud-admin`. Never expose or commit access keys.

### Important AWS CLI Commands

Replace `YOUR_BUCKET_NAME` with the actual bucket name.

**1. List all buckets**

```powershell
aws s3 ls --profile cloud-admin
```

**2. List objects in a bucket**

```powershell
aws s3 ls s3://YOUR_BUCKET_NAME/ --profile cloud-admin
```

**3. Upload a file**

```powershell
aws s3 cp employees.csv s3://YOUR_BUCKET_NAME/active/ --profile cloud-admin
```

**4. Download a file**

```powershell
aws s3 cp s3://YOUR_BUCKET_NAME/active/employees.csv ./employees.csv --profile cloud-admin
```

**5. Upload an entire directory**

```powershell
aws s3 sync ./uploads/ s3://YOUR_BUCKET_NAME/active/ --profile cloud-admin
```

### Useful S3 API Commands

**Check bucket versioning**

```powershell
aws s3api get-bucket-versioning --bucket YOUR_BUCKET_NAME --profile cloud-admin
```

**List object versions**

```powershell
aws s3api list-object-versions --bucket YOUR_BUCKET_NAME --profile cloud-admin
```

**Check encryption**

```powershell
aws s3api get-bucket-encryption --bucket YOUR_BUCKET_NAME --profile cloud-admin
```

**Check lifecycle configuration**

```powershell
aws s3api get-bucket-lifecycle-configuration --bucket YOUR_BUCKET_NAME --profile cloud-admin
```

**Important Difference:**

| AWS S3 | AWS S3API |
|---|---|
| High-level commands | Low-level service API commands |
| Simplifies file operations | Provides access to specific S3 API operations |
| Used for upload, download and sync | Used to inspect and manage configurations |

---

## 6. Important AWS Concepts Learned

| Concept | What We Learned |
|---|---|
| Amazon S3 | Cloud object storage |
| Bucket | Container for storing objects |
| Object | File and metadata |
| Object Key | Unique object identifier within a bucket |
| Prefix | Logical object organization |
| Storage Classes | Different storage and retrieval options |
| Versioning | Preserving previous object versions |
| Delete Marker | Logical deletion in a versioned bucket |
| Lifecycle Policies | Automated object transitions |
| IAM | Identity and permission management |
| IAM Role | Temporary credentials for AWS resources |
| Bucket Policy | Resource-level access control |
| SSE-S3 | Encryption at rest |
| HTTPS/TLS | Encryption in transit |
| AWS CLI | Command-line interaction with AWS |

---

## 7. Important Interview Questions

**1. What is Amazon S3?**

Amazon S3 is an AWS object storage service used to store and retrieve data.

**2. What is the difference between a bucket and an object?**

A bucket is a container, while an object is the actual file stored inside it.

**3. What happens when we upload the same file again with Versioning enabled?**

S3 creates a new version and preserves the previous version.

**4. What is a Delete Marker?**

A Delete Marker is a special marker created when a versioned object is normally deleted. It makes the object appear deleted while previous versions remain stored.

**5. What are S3 Storage Classes?**

Storage Classes determine the storage characteristics, retrieval options and pricing of objects.

**6. Difference between Standard and Standard-IA?**

Standard is intended for frequently accessed data, whereas Standard-IA is intended for infrequently accessed data that still needs rapid retrieval.

**7. What is a Lifecycle Policy?**

A Lifecycle Policy automatically transitions or expires objects according to configured rules.

**8. What is the difference between IAM Policy and Bucket Policy?**

IAM Policies are attached to identities. Bucket Policies are attached to S3 resources.

**9. What is SSE-S3?**

Server-Side Encryption with Amazon S3 Managed Keys. S3 manages encryption keys and encrypts objects at rest.

**10. Difference between S3 and EBS?**

S3 is object storage, while EBS provides block storage volumes that can be attached to EC2 instances.

**11. What is the difference between AWS CLI and AWS Console?**

AWS Console provides a graphical interface, while AWS CLI allows us to interact with AWS through terminal commands.

**12. Is S3 Versioning a backup strategy?**

Versioning helps recover older object versions, but it is not a complete backup strategy. Additional protection and recovery mechanisms may be needed.

---

## 8. Cost Management and Cleanup

Before finishing the project, check AWS billing.

Important cost considerations:

- S3 Standard storage charges.
- Storage charges for noncurrent versions.
- Lifecycle transition requests.
- Retrieval charges.
- Minimum storage-duration charges for certain storage classes.

For this learning project:

- Keep Block Public Access enabled.
- Avoid unnecessary data uploads.
- Do not configure permanent deletion unless required.
- Monitor AWS Billing and Cost Explorer.
- Delete unnecessary test objects and versions only after completing the exercises.

---

## 9. Final Project Outcome

Through this project, we learned how to create and manage cloud object storage using Amazon S3.

We implemented:

- Bucket creation and configuration.
- CSV and JSON uploads.
- Object organization using prefixes.
- Versioning and recovery.
- Lifecycle transitions.
- IAM-based permissions.
- Bucket Policies.
- Encryption.
- AWS CLI file operations.

**Key Learning:** Amazon S3 is not just a place to upload files. It provides object versioning, automated storage management, security, access control and integration with other AWS services.

---

## 10. Future Improvements

Possible extensions to this project:

- Integrate S3 with an EC2-hosted application.
- Upload files using Python and Boto3.
- Create presigned URLs for temporary file access.
- Configure S3 event notifications.
- Integrate S3 with AWS Lambda.
- Build a data lake using Raw, Curated and Trusted prefixes.

These are future enhancements and are not part of the current implementation.