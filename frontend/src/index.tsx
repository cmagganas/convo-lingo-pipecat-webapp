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
            url: 'https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/uOTBlSKJsEKj257tmEnH',
            token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyIjoidU9UQmxTS0pzRUtqMjU3dG1FbkgiLCJvIjp0cnVlLCJkIjoiZWNkN2Y2ZTEtYzBiMC00NTcyLTg1ZTItNzA4MGU0OTE5ZDQ3IiwiaWF0IjoxNzU1ODE4MTU4fQ.JDUUgEIm1lu1C-0GHO7tqomfWFiKe4hsSrXBnH95nUk'
          }}
        />
      </FullScreenContainer>
    </ThemeProvider>
  </StrictMode>
);
