import { it,expect } from 'vitest';
import { render,screen,fireEvent,cleanup } from '@testing-library/react';
import { HashRouter } from 'react-router-dom';
import { Start } from '../src/pages/Start';
import { database,storage,useStore } from '../src/state/store';
it('edits tile sizes and writes IndexedDB',async()=>{render(<HashRouter><Start/></HashRouter>);fireEvent.click(screen.getByText('personalize'));fireEvent.click(screen.getByLabelText('Edit ZeroSchedule'));fireEvent.change(screen.getByLabelText('Size'),{target:{value:'small'}});expect(useStore.getState().tiles[0].size).toBe('small');await storage.setItem('test-layout',JSON.stringify(useStore.getState().tiles));expect(JSON.parse((await database.settings.get('test-layout'))!.value)[0].size).toBe('small');cleanup();});
