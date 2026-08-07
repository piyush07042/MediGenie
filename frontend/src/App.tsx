import { Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import AppShell from "./layouts/AppShell";
import LoadingOverlay from "./components/LoadingOverlay";

function App() {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const isPublicRoute = location.pathname === "/login" || location.pathname === "/register";

  // Show a brief loading overlay on route change
  useEffect(() => {
    setLoading(true);
    // hide after paint/short delay
    const id = window.setTimeout(() => setLoading(false), 300);
    return () => window.clearTimeout(id);
  }, [location.pathname]);

  if (isPublicRoute) {
    return (
      <>
        <LoadingOverlay visible={loading} />
        <Outlet />
      </>
    );
  }

  return (
    <AppShell>
      <LoadingOverlay visible={loading} />
      <Outlet />
    </AppShell>
  );
}

export default App;
