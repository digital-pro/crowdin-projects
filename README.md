# ResNet-50 Vocabulary Classifier

A web-based image classification tool that uses ResNet-50 to classify objects in vocabulary images with precise grid detection.

## Features

- **ResNet-50 Classification**: Uses pre-trained ResNet-50 model via TensorFlow.js
- **Grid Detection**: Automatically detects 2x2 grids in vocabulary images
- **Vocabulary Matching**: Matches predictions against a curated 171-word vocabulary list
- **Interactive Interface**: Click on grid cells to classify individual sections
- **CORS Proxy**: Built-in proxy for handling cross-origin image requests

## Vocabulary

The classifier works with a curated vocabulary of 171 words including:
- Common objects (acorn, ball, fork, wheel)
- Animals (bear, duck, kitten, turtle, panda)
- Food items (cake, cheese, pie, watermelon)
- Tools and equipment (blender, telescope, typewriter)
- Specialized terms (paleontologist, metronome, gesticulate)

## Local Development

### Prerequisites
- Node.js (v14 or higher)
- Modern web browser

### Running Locally

1. Clone the repository
2. Navigate to the project directory
3. Start the local server:
   ```bash
   node serve-resnet.js
   ```
4. Open your browser and go to `http://localhost:8080`

The application will automatically load the ResNet-50 model and vocabulary list.

## Deployment to Vercel

### Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/resnet-vocab-classifier)

### Manual Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Follow the prompts**:
   - Choose your project name
   - Select your Vercel account/team
   - The deployment will be automatically configured using `vercel.json`

### Configuration

The project includes a `vercel.json` configuration file that:
- Sets up serverless functions for the CORS proxy
- Configures static file serving
- Sets up proper routing for the application

### Environment Variables

No environment variables are required for basic functionality.

## How It Works

1. **Model Loading**: The application loads a pre-trained ResNet-50 model from TensorFlow.js
2. **Image Processing**: Images are loaded through the CORS proxy and processed for grid detection
3. **Grid Detection**: The system automatically detects 2x2 grids in vocabulary images using reference coordinates
4. **Classification**: Each grid cell is extracted, resized to 224x224, and classified using ResNet-50
5. **Vocabulary Matching**: Predictions are matched against the 171-word vocabulary list
6. **Results Display**: Results are displayed with confidence scores and vocabulary matches highlighted

## API Endpoints

### `/api/proxy`
CORS proxy for loading images from external sources.

**Parameters:**
- `url` (required): The URL of the image to proxy

**Example:**
```
GET /api/proxy?url=https://example.com/image.jpg
```

## File Structure

```
├── real-imagenet-resnet.html    # Main application
├── serve-resnet.js              # Local development server
├── api/
│   └── proxy.js                 # Vercel serverless function for CORS proxy
├── vocab/
│   └── vocab_list.txt           # 171-word vocabulary list
├── vercel.json                  # Vercel deployment configuration
├── package.json                 # Project metadata
└── README.md                    # This file
```

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Performance Notes

- Model loading may take 10-30 seconds on first load
- Classification speed depends on device capabilities
- Grid detection is optimized for vocabulary test images

## Troubleshooting

### Model Loading Issues
- Ensure you have a stable internet connection
- Try refreshing the page if the model fails to load
- Check browser console for detailed error messages

### Image Loading Issues
- Images are loaded through the CORS proxy
- If images fail to load, check the proxy endpoint status
- Ensure the image URLs are accessible

### Classification Issues
- Make sure the model is fully loaded before attempting classification
- Grid detection works best with standard vocabulary test images
- Some images may be skipped if they don't follow the standard grid format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally using `node serve-resnet.js`
5. Submit a pull request

## License

MIT License - see LICENSE file for details 