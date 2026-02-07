# Behavior Testing Skill

## Trigger
- Nach Feature-Implementation
- Wenn Tests nur DOM-Rendering pruefen ("smoke tests")
- Wenn Code-Review Luecken in der Test-Abdeckung findet
- `/behavior-tests` Slash-Command

## Problem
Standard-Tests (via AI-Generation oder Copilot) pruefen oft nur "wird gerendert?", nicht "funktioniert es?". Das fuehrt zu:
- Buttons ohne Funktionalitaet bestehen alle Tests
- API-Aufrufe mit falschen Argumenten werden nie erkannt
- State-Verlust bei Navigation/Re-Mount bleibt unsichtbar
- Fehlende Error-UI wird nie getestet

## 4 Test-Kategorien (PFLICHT)

### 1. API-Contract Tests
**Was:** Verifiziere, dass API-Funktionen mit den richtigen Argumenten aufgerufen werden.
**Warum:** Falsche Argumente (fehlende Language-Parameter, falsche Endpoints) sind unsichtbar in Rendering-Tests.

```typescript
// SCHLECHT: Prueft nur DOM
it('sends message', async () => {
  await sendMessage('hello');
  expect(screen.getByText('hello')).toBeInTheDocument(); // DOM only!
});

// GUT: Prueft API-Contract
it('sends message with correct language', async () => {
  await sendMessage('hello');
  expect(mockApi).toHaveBeenCalledWith(
    'hello',
    expect.any(Array),   // history
    'en',                 // language code
  );
});
```

**Checkliste:**
- [ ] Mock der API-Funktion mit `vi.fn()`
- [ ] Pruefe Aufruf-Argumente mit `toHaveBeenCalledWith`
- [ ] Pruefe Anzahl der Aufrufe mit `toHaveBeenCalledTimes`
- [ ] Pruefe was bei API-Fehler passiert (Error-UI sichtbar?)

### 2. State-Persistence Tests
**Was:** Verifiziere, dass State nach Re-Mount, Page-Refresh oder Auth-Wechsel korrekt bleibt.
**Warum:** sessionStorage/localStorage-Bugs, Zustand-Resets bei Login/Logout.

```typescript
// Prueft sessionStorage-Persistenz
it('persists counter to sessionStorage', async () => {
  render(<Chat />);
  await sendMessage('test');
  expect(sessionStorage.getItem('key')).toBe('1');
});

// Prueft Auth-Transition
it('resets counter on login', () => {
  sessionStorage.setItem('key', '5');
  useAuthStore.setState({ isAuthenticated: true });
  // Effect should reset
  expect(sessionStorage.getItem('key')).toBe('0');
});
```

**Checkliste:**
- [ ] sessionStorage/localStorage vor und nach Aktionen pruefen
- [ ] Auth-State-Wechsel testen (logged-in -> logged-out und umgekehrt)
- [ ] Zustand-Store direkt mit `setState` manipulieren fuer Edge-Cases
- [ ] Default-State nach Store-Reset pruefen

### 3. Error-Boundary Tests
**Was:** Verifiziere, dass Fehler dem User angezeigt werden und die App nicht crasht.
**Warum:** Fehlende Error-UI ist die haeufigste UX-Luecke.

```typescript
// API-Fehler -> Error-UI
it('shows error on checkout failure', async () => {
  mockPost.mockRejectedValueOnce(new Error('Server error'));
  fireEvent.click(checkoutButton);
  await waitFor(() => {
    expect(screen.getByText(/error|fehler/i)).toBeInTheDocument();
  });
});

// 204 No Content -> kein Crash
it('handles 204 No Content', async () => {
  mockFetch({ ok: true, status: 204, text: () => Promise.resolve('') });
  const result = await apiClient.get('/api/logout');
  expect(result).toEqual({});
});
```

**Checkliste:**
- [ ] API-Rejection -> Error-Message sichtbar
- [ ] Leere Responses (204, empty body) -> kein Crash
- [ ] Rate-Limit (429) -> Retry-Info angezeigt
- [ ] Non-JSON Error-Body -> graceful degradation

### 4. Security-Boundary Tests
**Was:** Verifiziere Input-Validation, Auth-Gates und Redirect-Sicherheit.
**Warum:** XSS-Praevention, Open-Redirect-Verhinderung, Rate-Limit-Enforcement.

```typescript
// Input-Laenge
it('rejects input over 2000 chars', async () => {
  await sendMessage('a'.repeat(2001));
  expect(mockApi).not.toHaveBeenCalled();
  expect(screen.getByText(/maximum/i)).toBeInTheDocument();
});

// URL-Validation
it('blocks non-stripe.com redirect URLs', async () => {
  mockPost.mockResolvedValueOnce({ url: 'https://evil.com/steal' });
  fireEvent.click(checkoutButton);
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });
});

// CSRF-Token
it('attaches CSRF token to POST but not GET', async () => {
  document.cookie = 'csrf_token=abc123';
  await apiClient.post('/api/data', {});
  expect(fetchMock).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({
      headers: expect.objectContaining({ 'X-CSRF-Token': 'abc123' }),
    }),
  );
});
```

**Checkliste:**
- [ ] Input-Laenge-Limits werden client-seitig enforced
- [ ] Auth-Gate blockiert unauthentifizierte User
- [ ] Plan-Gate blockiert Free-Plan bei Premium-Features
- [ ] Redirect-URLs werden auf erlaubte Domains geprueft
- [ ] CSRF-Token wird bei POST angehaengt, nicht bei GET
- [ ] Credentials: 'include' auf allen Requests

## Implementierungs-Workflow

1. **Identifiziere Luecken**: Lies bestehende Tests. Pruefe ob sie nur `toBeInTheDocument()` nutzen.
2. **Mock die APIs**: `vi.mock()` fuer Service-Module, `vi.fn()` fuer einzelne Funktionen.
3. **Setze State direkt**: `useAuthStore.setState({...})` statt ueber UI navigieren.
4. **Pruefe Aufrufe**: `toHaveBeenCalledWith()` ist wichtiger als `toBeInTheDocument()`.
5. **Teste Fehlerpfade**: Jeder `try/catch` im Produktionscode braucht einen Test.

## Dateibenennung

```
# Bestehende Rendering-Tests behalten:
ComponentName.test.tsx

# Neue Behavior-Tests daneben:
ComponentName.behavior.test.tsx

# Oder in describe-Bloecken trennen:
describe('rendering', () => { ... });   // bestehend
describe('behavior', () => { ... });    // neu
describe('error handling', () => { ... }); // neu
```

## Anti-Patterns

| Anti-Pattern | Problem | Loesung |
|-------------|---------|---------|
| Nur `toBeInTheDocument()` | Prueft nicht ob Button funktioniert | `toHaveBeenCalledWith()` |
| Kein API-Mock | Test ruft echte API auf | `vi.mock()` + `vi.fn()` |
| Happy-Path only | Fehler-UI wird nie getestet | `mockRejectedValueOnce()` |
| State-Annahmen | Store wird nicht zurueckgesetzt | `beforeEach` + `setState` |
| Kein Auth-Kontext | Tests laufen nur als eingeloggt | Teste beide Zustaende |

## Referenz-Implementierung

Siehe: `Website/Relaunch 2026 01/services/__tests__/apiClient.test.ts` (Error-Boundary + Security-Boundary Muster)
Siehe: `Website/Relaunch 2026 01/components/__tests__/MultilingualChat.behavior.test.tsx` (API-Contract + State-Persistence Muster)
