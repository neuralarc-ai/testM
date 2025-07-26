import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Title,
  Paragraph,
  ActivityIndicator,
} from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../theme/theme';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading, error, clearError } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    clearError();
    const result = await login(email, password);
    
    if (!result.success) {
      Alert.alert('Login Failed', result.error || 'Please check your credentials');
    }
  };

  const navigateToRegister = () => {
    navigation.navigate('Register');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.content}>
          {/* Logo/Header */}
          <View style={styles.header}>
            <Title style={styles.title}>Manus AI</Title>
            <Paragraph style={styles.subtitle}>
              Your Autonomous AI Assistant
            </Paragraph>
          </View>

          {/* Login Form */}
          <Card style={styles.card}>
            <Card.Content>
              <Title style={styles.cardTitle}>Sign In</Title>
              
              <TextInput
                label="Email"
                value={email}
                onChangeText={setEmail}
                mode="outlined"
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                style={styles.input}
                disabled={loading}
              />

              <TextInput
                label="Password"
                value={password}
                onChangeText={setPassword}
                mode="outlined"
                secureTextEntry={!showPassword}
                right={
                  <TextInput.Icon
                    icon={showPassword ? 'eye-off' : 'eye'}
                    onPress={() => setShowPassword(!showPassword)}
                  />
                }
                style={styles.input}
                disabled={loading}
              />

              {error && (
                <Text style={styles.errorText}>{error}</Text>
              )}

              <Button
                mode="contained"
                onPress={handleLogin}
                style={styles.loginButton}
                disabled={loading}
                loading={loading}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>

              <Button
                mode="text"
                onPress={navigateToRegister}
                style={styles.registerButton}
                disabled={loading}
              >
                Don't have an account? Sign Up
              </Button>
            </Card.Content>
          </Card>

          {/* Features */}
          <View style={styles.features}>
            <Text style={styles.featuresTitle}>What you can do with Manus AI:</Text>
            <View style={styles.featureItem}>
              <Text style={styles.featureText}>🤖 11 Specialized AI Agents</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureText}>🎨 Content & Media Generation</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureText}>🌐 Web Automation & Control</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureText}>📊 Data Analysis & Insights</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureText}>⚡ Real-time Task Orchestration</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: theme.spacing.md,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.secondary,
    textAlign: 'center',
  },
  card: {
    marginBottom: theme.spacing.lg,
    ...theme.shadows.medium,
  },
  cardTitle: {
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
    color: theme.colors.primary,
  },
  input: {
    marginBottom: theme.spacing.md,
  },
  errorText: {
    color: theme.colors.error,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  loginButton: {
    marginTop: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  registerButton: {
    marginTop: theme.spacing.sm,
  },
  features: {
    marginTop: theme.spacing.lg,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
    textAlign: 'center',
  },
  featureItem: {
    marginBottom: theme.spacing.sm,
  },
  featureText: {
    fontSize: 14,
    color: theme.colors.secondary,
    textAlign: 'center',
  },
});

