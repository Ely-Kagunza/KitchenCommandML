# React + TypeScript Complete Guide

## Table of Contents

1. [Setup & Installation](#setup--installation)
2. [TypeScript Basics](#typescript-basics)
3. [React Components](#react-components)
4. [Hooks](#hooks)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Type Definitions](#type-definitions)
8. [Best Practices](#best-practices)
9. [Common Patterns](#common-patterns)
10. [Project Structure](#project-structure)

---

## Setup & Installation

### Create a New React + TypeScript Project

```bash
# Using Vite (recommended)
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# Or using Create React App
npx create-react-app my-app --template typescript
cd my-app
npm install
```

### Install Essential Dependencies

```bash
npm install react react-dom
npm install -D typescript @types/react @types/react-dom
npm install @tanstack/react-query axios
npm install recharts
npm install tailwindcss postcss autoprefixer
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Project Structure

```
src/
├── components/
│   ├── common/
│   ├── kitchen/
│   ├── demand/
│   ├── customer/
│   └── inventory/
├── pages/
├── hooks/
├── services/
├── types/
├── utils/
├── App.tsx
└── main.tsx
```

---

## TypeScript Basics

### Basic Types

```typescript
// Primitives
const name: string = 'John'
const age: number = 30
const isActive: boolean = true
const nothing: null = null
const undefined_value: undefined = undefined

// Arrays
const numbers: number[] = [1, 2, 3]
const strings: Array<string> = ['a', 'b', 'c']
const mixed: (string | number)[] = [1, 'two', 3]

// Tuples
const tuple: [string, number] = ['hello', 42]

// Any (avoid when possible)
let anything: any = 'can be anything'

// Union Types
type Status = 'success' | 'error' | 'loading'
const status: Status = 'success'

// Intersection Types
type Admin = { role: 'admin' }
type User = { name: string }
type AdminUser = Admin & User
```

### Interfaces vs Types

```typescript
// Interface (preferred for objects)
interface User {
  id: number
  name: string
  email: string
  isActive?: boolean // optional
}

// Type (more flexible)
type UserType = {
  id: number
  name: string
  email: string
}

// Extending interfaces
interface Admin extends User {
  role: 'admin'
  permissions: string[]
}

// Extending types
type AdminType = UserType & {
  role: 'admin'
}
```

### Generics

```typescript
// Generic function
function getFirstElement<T>(arr: T[]): T {
  return arr[0]
}

const firstNum = getFirstElement<number>([1, 2, 3]) // number
const firstStr = getFirstElement<string>(['a', 'b']) // string

// Generic interface
interface Container<T> {
  value: T
  getValue(): T
}

const numberContainer: Container<number> = {
  value: 42,
  getValue() {
    return this.value
  },
}

// Generic with constraints
function merge<T extends object>(obj1: T, obj2: T): T {
  return { ...obj1, ...obj2 }
}
```

---

## React Components

### Functional Components with TypeScript

```typescript
// Basic component
interface Props {
  title: string;
  count: number;
  onIncrement: () => void;
}

const Counter: React.FC<Props> = ({ title, count, onIncrement }) => {
  return (
    <div>
      <h1>{title}</h1>
      <p>Count: {count}</p>
      <button onClick={onIncrement}>Increment</button>
    </div>
  );
};

export default Counter;
```

### Component with Children

```typescript
interface CardProps {
  title: string;
  children: React.ReactNode; // accepts any valid React content
}

const Card: React.FC<CardProps> = ({ title, children }) => {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-content">{children}</div>
    </div>
  );
};

// Usage
<Card title="My Card">
  <p>This is the content</p>
</Card>
```

### Component with Event Handlers

```typescript
interface FormProps {
  onSubmit: (data: FormData) => void;
}

interface FormData {
  email: string;
  password: string;
}

const LoginForm: React.FC<FormProps> = ({ onSubmit }) => {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    onSubmit({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" required />
      <input type="password" name="password" required />
      <button type="submit">Login</button>
    </form>
  );
};
```

### Component with Refs

```typescript
interface TextInputProps {
  placeholder: string;
}

const TextInput = React.forwardRef<HTMLInputElement, TextInputProps>(
  ({ placeholder }, ref) => (
    <input ref={ref} placeholder={placeholder} />
  )
);

TextInput.displayName = "TextInput";

// Usage
const App = () => {
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.focus();
  };

  return (
    <>
      <TextInput ref={inputRef} placeholder="Type here" />
      <button onClick={handleClick}>Focus Input</button>
    </>
  );
};
```

---

## Hooks

### useState

```typescript
import { useState } from "react";

interface User {
  id: number;
  name: string;
}

const UserProfile = () => {
  // Explicit type
  const [user, setUser] = useState<User | null>(null);

  // Type inference
  const [count, setCount] = useState(0); // inferred as number
  const [name, setName] = useState(""); // inferred as string

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};
```

### useEffect

```typescript
import { useEffect, useState } from "react";

interface Post {
  id: number;
  title: string;
  body: string;
}

const PostList = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await fetch("https://api.example.com/posts");
        const data: Post[] = await response.json();
        setPosts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []); // dependency array

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
};
```

### useContext

```typescript
import { createContext, useContext, ReactNode } from "react";

interface Theme {
  primary: string;
  secondary: string;
}

const ThemeContext = createContext<Theme | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  theme: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  theme,
}) => (
  <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
);

export const useTheme = (): Theme => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
};

// Usage
const Button = () => {
  const theme = useTheme();
  return <button style={{ color: theme.primary }}>Click me</button>;
};
```

### useReducer

```typescript
import { useReducer } from "react";

interface State {
  count: number;
  error: string | null;
}

type Action =
  | { type: "INCREMENT" }
  | { type: "DECREMENT" }
  | { type: "RESET" }
  | { type: "SET_ERROR"; payload: string };

const initialState: State = {
  count: 0,
  error: null,
};

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "INCREMENT":
      return { ...state, count: state.count + 1 };
    case "DECREMENT":
      return { ...state, count: state.count - 1 };
    case "RESET":
      return { ...state, count: 0 };
    case "SET_ERROR":
      return { ...state, error: action.payload };
    default:
      return state;
  }
};

const Counter = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: "INCREMENT" })}>+</button>
      <button onClick={() => dispatch({ type: "DECREMENT" })}>-</button>
      <button onClick={() => dispatch({ type: "RESET" })}>Reset</button>
    </div>
  );
};
```

### Custom Hooks

```typescript
import { useState, useCallback } from "react";

interface UseToggleReturn {
  isOpen: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
}

const useToggle = (initialState: boolean = false): UseToggleReturn => {
  const [isOpen, setIsOpen] = useState(initialState);

  const toggle = useCallback(() => setIsOpen((prev) => !prev), []);
  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);

  return { isOpen, toggle, open, close };
};

// Usage
const Modal = () => {
  const { isOpen, toggle, close } = useToggle();

  return (
    <>
      <button onClick={toggle}>Open Modal</button>
      {isOpen && (
        <div className="modal">
          <p>Modal Content</p>
          <button onClick={close}>Close</button>
        </div>
      )}
    </>
  );
};
```

---

## State Management

### TanStack Query (React Query)

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

interface Post {
  id: number;
  title: string;
  body: string;
}

// Fetch hook
const usePosts = () => {
  return useQuery({
    queryKey: ["posts"],
    queryFn: async () => {
      const { data } = await axios.get<Post[]>("/api/posts");
      return data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Mutation hook
const useCreatePost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newPost: Omit<Post, "id">) => {
      const { data } = await axios.post<Post>("/api/posts", newPost);
      return data;
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
  });
};

// Component
const PostList = () => {
  const { data: posts, isLoading, error } = usePosts();
  const createPost = useCreatePost();

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <ul>
        {posts?.map((post) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
      <button
        onClick={() =>
          createPost.mutate({
            title: "New Post",
            body: "Content here",
          })
        }
      >
        Add Post
      </button>
    </div>
  );
};
```

### Zustand (Alternative)

```typescript
import { create } from "zustand";

interface Store {
  count: number;
  increment: () => void;
  decrement: () => void;
}

const useStore = create<Store>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}));

// Usage
const Counter = () => {
  const { count, increment, decrement } = useStore();

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
};
```

---

## API Integration

### Service Layer

```typescript
// services/api.ts
import axios, { AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

### Kitchen Service

```typescript
// services/kitchenService.ts
import api from './api'

export interface PrepTimePrediction {
  station_id: string
  menu_item_id: number
  predicted_prep_time_minutes: number
  lower_bound_minutes: number
  upper_bound_minutes: number
  confidence: number
}

export interface BatchPrediction {
  batch_size: number
  item_predictions: PrepTimePrediction[]
  estimated_total_time_minutes: number
  generated_at: string
}

export const kitchenService = {
  predictPrepTime: async (
    restaurantId: string,
    stationId: string,
    menuItemId: number,
  ): Promise<PrepTimePrediction> => {
    const { data } = await api.post('/predictions/kitchen/prep-time', {
      restaurant_id: restaurantId,
      station_id: stationId,
      menu_item_id: menuItemId,
    })
    return data
  },

  predictBatchPrepTime: async (
    restaurantId: string,
    orders: Array<{ station_id: string; menu_item_id: number }>,
  ): Promise<BatchPrediction> => {
    const { data } = await api.post('/predictions/kitchen/batch-prep-time', {
      restaurant_id: restaurantId,
      orders,
    })
    return data
  },

  getBottlenecks: async (restaurantId: string) => {
    const { data } = await api.get('/predictions/kitchen/bottlenecks', {
      params: { restaurant_id: restaurantId },
    })
    return data
  },

  getStationPerformance: async (restaurantId: string) => {
    const { data } = await api.get('/predictions/kitchen/station-performance', {
      params: { restaurant_id: restaurantId },
    })
    return data
  },
}
```

### Custom Hook for API

```typescript
// hooks/useKitchenPredictions.ts
import { useQuery } from '@tanstack/react-query'
import { kitchenService } from '../services/kitchenService'

export const usePrepTimePrediction = (
  restaurantId: string,
  stationId: string,
  menuItemId: number,
) => {
  return useQuery({
    queryKey: ['prepTime', restaurantId, stationId, menuItemId],
    queryFn: () =>
      kitchenService.predictPrepTime(restaurantId, stationId, menuItemId),
    enabled: !!restaurantId && !!stationId && menuItemId > 0,
  })
}

export const useBottlenecks = (restaurantId: string) => {
  return useQuery({
    queryKey: ['bottlenecks', restaurantId],
    queryFn: () => kitchenService.getBottlenecks(restaurantId),
    enabled: !!restaurantId,
  })
}
```

---

## Type Definitions

### Create Type Files

```typescript
// types/kitchen.ts
export interface Station {
  id: string
  name: string
  total_items_prepared: number
  avg_prep_time_minutes: number
  within_5_min_accuracy: number
}

export interface MenuItem {
  id: number
  name: string
  category: string
  avg_prep_time: number
}

export interface Bottleneck {
  station_id: string
  station_name: string
  avg_prep_time: number
  bottleneck_threshold: number
  slow_items: SlowItem[]
}

export interface SlowItem {
  menu_item_id: number
  avg_prep_time: number
  occurences: number
}
```

```typescript
// types/demand.ts
export interface DemandForecast {
  timestamp: string
  hour: number
  predicted_orders: number
  confidence: number
}

export interface DailyForecast {
  date: string
  day_of_week: string
  predicted_orders: number
  hourly_breakdown: number[]
  confidence: number
}

export interface PeakHour {
  hour: number
  predicted_orders: number
}
```

```typescript
// types/customer.ts
export interface ChurnPrediction {
  customer_id: number
  churn_probability: number
  risk_segment: 'low_risk' | 'medium_risk' | 'high_risk'
  will_churn: number
  confidence: number
}

export interface LTVPrediction {
  customer_id: number
  predicted_ltv: number
  ltv_segment: 'low_value' | 'medium_value' | 'high_value'
  confidence: number
}
```

---

## Best Practices

### 1. Component Organization

```typescript
// ✅ Good: Clear structure
interface Props {
  title: string;
  onClose: () => void;
}

const Modal: React.FC<Props> = ({ title, onClose }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      // do something
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal">
      <h2>{title}</h2>
      <button onClick={onClose}>Close</button>
    </div>
  );
};

export default Modal;
```

### 2. Error Handling

```typescript
// ✅ Good: Proper error handling
const useFetchData = <T>(url: string) => {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result: T = await response.json()
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [url])

  return { data, error, loading }
}
```

### 3. Memoization

```typescript
import { memo, useMemo, useCallback } from "react";

interface ListProps {
  items: string[];
  onItemClick: (item: string) => void;
}

// ✅ Memoize component to prevent unnecessary re-renders
const ListItem = memo<{ item: string; onClick: () => void }>(
  ({ item, onClick }) => (
    <li onClick={onClick}>{item}</li>
  )
);

const List: React.FC<ListProps> = ({ items, onItemClick }) => {
  // ✅ Memoize callback
  const handleClick = useCallback(
    (item: string) => {
      onItemClick(item);
    },
    [onItemClick]
  );

  // ✅ Memoize computed value
  const sortedItems = useMemo(() => {
    return [...items].sort();
  }, [items]);

  return (
    <ul>
      {sortedItems.map((item) => (
        <ListItem
          key={item}
          item={item}
          onClick={() => handleClick(item)}
        />
      ))}
    </ul>
  );
};
```

### 4. Type Safety

```typescript
// ✅ Good: Strict typing
interface User {
  id: number;
  name: string;
  email: string;
}

const UserCard: React.FC<{ user: User }> = ({ user }) => {
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
};

// ❌ Bad: Using any
const UserCard: React.FC<{ user: any }> = ({ user }) => {
  return <div>{user.name}</div>;
};
```

---

## Common Patterns

### Loading States

```typescript
interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

const useAsync = <T>(
  asyncFunction: () => Promise<T>,
  immediate = true,
): AsyncState<T> & { execute: () => Promise<void> } => {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  })

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null })
    try {
      const response = await asyncFunction()
      setState({ data: response, loading: false, error: null })
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      })
    }
  }, [asyncFunction])

  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [execute, immediate])

  return { ...state, execute }
}
```

### Form Handling

```typescript
interface FormState {
  email: string;
  password: string;
}

const useForm = <T extends Record<string, any>>(initialValues: T) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Partial<T>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (onSubmit: (values: T) => void) => {
    return (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(values);
    };
  };

  const reset = () => setValues(initialValues);

  return { values, errors, handleChange, handleSubmit, reset };
};

// Usage
const LoginForm = () => {
  const { values, handleChange, handleSubmit } = useForm<FormState>({
    email: "",
    password: "",
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input
        name="email"
        value={values.email}
        onChange={handleChange}
      />
      <input
        name="password"
        type="password"
        value={values.password}
        onChange={handleChange}
      />
      <button type="submit">Login</button>
    </form>
  );
};
```

---

## Project Structure

### Recommended Layout

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── index.ts
│   │   ├── kitchen/
│   │   │   ├── PrepTimeChart.tsx
│   │   │   ├── BottleneckTable.tsx
│   │   │   ├── StationPerformance.tsx
│   │   │   └── index.ts
│   │   ├── demand/
│   │   ├── customer/
│   │   ├── inventory/
│   │   └── models/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── KitchenPage.tsx
│   │   ├── DemandPage.tsx
│   │   ├── CustomerPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── ModelsPage.tsx
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useKitchenPredictions.ts
│   │   ├── useDemandPredictions.ts
│   │   ├── useCustomerPredictions.ts
│   │   ├── useInventoryPredictions.ts
│   │   ├── useModelTraining.ts
│   │   └── index.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── kitchenService.ts
│   │   ├── demandService.ts
│   │   ├── customerService.ts
│   │   ├── inventoryService.ts
│   │   ├── modelService.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── kitchen.ts
│   │   ├── demand.ts
│   │   ├── customer.ts
│   │   ├── inventory.ts
│   │   ├── models.ts
│   │   └── index.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   └── index.ts
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── index.css
├── public/
├── .env
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

### Index Files for Clean Imports

```typescript
// components/kitchen/index.ts
export { default as PrepTimeChart } from './PrepTimeChart'
export { default as BottleneckTable } from './BottleneckTable'
export { default as StationPerformance } from './StationPerformance'

// Usage: import { PrepTimeChart, BottleneckTable } from "@/components/kitchen";
```

---

## Configuration Files

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
```

---

## Summary

### Key Takeaways

1. **Always use TypeScript** - Catch errors at compile time
2. **Define interfaces** - For all data structures
3. **Use custom hooks** - For reusable logic
4. **Leverage TanStack Query** - For API state management
5. **Memoize wisely** - Only when necessary
6. **Keep components small** - Single responsibility
7. **Type your props** - Always define Props interface
8. **Handle errors** - Gracefully with try-catch
9. **Use service layer** - Separate API logic
10. **Organize by feature** - Not by type

### Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org)

---

**Happy coding! 🚀**
