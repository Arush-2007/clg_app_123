import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAp40xuv7HrNLu2mmFyW7hpVwGAlXeMRSc",
  authDomain: "college-app-835a2.firebaseapp.com",
  projectId: "college-app-835a2",
  storageBucket: "college-app-835a2.firebasestorage.app",
  messagingSenderId: "889736171626",
  appId: "1:889736171626:web:5dc175e241ab7799f7ba13",
};

const app = getApps().length ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(app);

export { app, auth };
