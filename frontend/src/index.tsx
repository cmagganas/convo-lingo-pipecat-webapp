import {
  ConsoleTemplate,
  FullScreenContainer,
  ThemeProvider,
} from '@pipecat-ai/voice-ui-kit';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

//@ts-ignore - fontsource-variable/geist is not typed
import '@fontsource-variable/geist';
//@ts-ignore - fontsource-variable/geist is not typed
import '@fontsource-variable/geist-mono';

createRoot(document.getElementById('root')!).render(
  // @ts-ignore
  <StrictMode>
    <ThemeProvider>
      <FullScreenContainer>
        <ConsoleTemplate
          transportType="daily"
          connectParams={{
            // @ts-ignore - import.meta.env works fine in Vite
            url: `${import.meta.env.VITE_DAILY_ROOM_URL}`, 
            // @ts-ignore - import.meta.env works fine in Vite
            token: `${import.meta.env.VITE_DAILY_ROOM_TOKEN}`
          }}
        />
      </FullScreenContainer>
    </ThemeProvider>
  </StrictMode>
);
