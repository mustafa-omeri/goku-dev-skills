---
title: Do Not Trigger State Updates in Effects Using Unstable Callbacks
impact: CRITICAL
impactDescription: prevents infinite re-render loops and browser crash (Maximum update depth exceeded)
tags: rerender, useEffect, callbacks, dependencies, infinite-loop, state-synchronization
---

## Do Not Trigger State Updates in Effects Using Unstable Callbacks

Calling a parent component's state updater or callback inside a child component's `useEffect` when that callback's reference changes on every render triggers an infinite re-render loop (`Warning: Maximum update depth exceeded`).

**Incorrect (unstable inline callback + effect synchronization):**

```tsx
// Parent passes inline arrow function
function Categories() {
  const [companyList, setCompanyList] = useState([]);
  return <CompanyBar onCompanyListChange={(companies) => setCompanyList(companies)} />;
}

// Child calls callback inside useEffect depending on that callback
function CompanyBar({ onCompanyListChange, companyName }) {
  useEffect(() => {
    onCompanyListChange([{ id: 1, companyName }]);
  }, [onCompanyListChange, companyName]); // ❌ Infinite loop: callback reference changes on every render!
}
```

**Correct (Approach 1: Pass identity-stable state setter directly):**

```tsx
// Parent passes the stable setState dispatcher directly
function Categories() {
  const [companyList, setCompanyList] = useState([]);
  return <CompanyBar onCompanyListChange={setCompanyList} />;
}
```

**Correct (Approach 2: Wrap callback in useCallback):**

```tsx
function Categories() {
  const [companyList, setCompanyList] = useState([]);
  const handleCompanyListChange = useCallback((companies) => {
    setCompanyList(companies);
  }, []);
  return <CompanyBar onCompanyListChange={handleCompanyListChange} />;
}
```

**Correct (Approach 3: Move state update out of useEffect into an event handler):**

```tsx
// Notify parent only when an event or action actually occurs
function CompanyBar({ onCompanyListChange }) {
  const handleSelect = (company) => {
    onCompanyListChange(company);
  };
  return <button onClick={handleSelect}>Select</button>;
}
```

**Correct (Approach 4: Decouple callback identity using useRef):**

```tsx
function CompanyBar({ onCompanyListChange, companyName }) {
  const callbackRef = useRef(onCompanyListChange);
  useEffect(() => {
    callbackRef.current = onCompanyListChange;
  });

  useEffect(() => {
    callbackRef.current([{ id: 1, companyName }]);
  }, [companyName]); // Callback is NOT in dependency array
}
```

Reference: [React docs: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
