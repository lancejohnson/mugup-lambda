# MugUp Lambda
Serverless AWS Lambda backend for scalable mug mockup rendering with the same custom deflection library.

## Why It Exists
The desktop version (mugup-local) works great for small batches, but rendering hundreds of mugs overwhelms local hardware. This serverless version provides unlimited scalability for high-volume production.

## What Makes It Interesting
- **Serverless scaling**: Handles thousands of concurrent mug renders without infrastructure management
- **Same deflection math**: Identical quadratic curve fitting and pixel transformations as the local version
- **Lambda-optimized**: Efficient S3 I/O and memory management for AWS Lambda constraints
- **Function chaining**: Orchestrates multiple Lambda functions for complex rendering pipelines

## Tech Stack
- **Runtime**: Python 3.x on AWS Lambda
- **Image Processing**: PIL/Pillow for graphics manipulation
- **Mathematics**: NumPy for quadratic curve fitting
- **Storage**: AWS S3 for input/output file management
- **Deployment**: Serverless Framework

## How to Run
```bash
git clone https://github.com/lancejohnson/mugup-lambda.git
cd mugup-lambda
npm install

# Deploy to AWS
serverless deploy

# Test locally
serverless invoke local --function render-and-upload-lastname-mug --data '{"lastname":{"lastname":"Johnson","niche":"test","item_name":"Test Mug","keywords":"test"}, "input_bucket":"your-bucket", "output_bucket":"your-bucket"}'
```

## Demo
API endpoints available after deployment. See handler.py for function signatures.

## Status
Production-ready - Deployed and serving real traffic.

## Notes
Built to complement mugup-local with cloud-native architecture. The mathematical deflection library is identical, ensuring consistent output between local and cloud versions.
