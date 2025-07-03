const builder = require('electron-builder');

// Simple build configuration without complex dependencies
const config = {
  appId: 'com.lyra.ai-assistant',
  productName: 'LYRA 3.0 AI Assistant',
  directories: {
    output: 'dist'
  },
  files: [
    'gui/**/*',
    'core/**/*',
    'config/**/*',
    'electron-main.js',
    'main.py',
    'launcher.py',
    'requirements.txt',
    'README.md',
    'package.json',
    '!node_modules',
    '!dist',
    '!.git',
    '!__pycache__',
    '!*.pyc',
    '!logs/**/*',
    '!upload/**/*'
  ],
  extraResources: [
    {
      from: 'main.py',
      to: 'backend/main.py'
    },
    {
      from: 'core',
      to: 'backend/core'
    },
    {
      from: 'launcher.py',
      to: 'backend/launcher.py'
    },
    {
      from: 'requirements.txt',
      to: 'backend/requirements.txt'
    }
  ],
  win: {
    target: [
      {
        target: 'nsis',
        arch: ['x64']
      },
      {
        target: 'portable',
        arch: ['x64']
      }
    ],
    artifactName: 'LYRA-3.0-Setup-${version}.${ext}',
    publisherName: 'LYRA Development Team',
    verifyUpdateCodeSignature: false
  },
  nsis: {
    oneClick: false,
    perMachine: false,
    allowToChangeInstallationDirectory: true,
    deleteAppDataOnUninstall: false,
    createDesktopShortcut: true,
    createStartMenuShortcut: true,
    shortcutName: 'LYRA 3.0'
  },
  portable: {
    artifactName: 'LYRA-3.0-Portable-${version}.${ext}'
  },
  compression: 'normal'
};

// Build function
async function build() {
  try {
    console.log('🚀 Building LYRA 3.0...');
    
    const result = await builder.build({
      targets: builder.Platform.WINDOWS.createTarget(['nsis', 'portable'], builder.Arch.x64),
      config
    });
    
    console.log('✅ Build completed successfully!');
    console.log('📁 Check the "dist" folder for installation files');
    
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

// Run build
build();
