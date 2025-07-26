import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, Button } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { theme } from '../theme/theme';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>Profile</Title>
            <Text>Name: {user?.name}</Text>
            <Text>Email: {user?.email}</Text>
            <Button mode="outlined" onPress={logout} style={styles.button}>
              Sign Out
            </Button>
          </Card.Content>
        </Card>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  content: { padding: theme.spacing.md },
  card: { marginBottom: theme.spacing.md },
  button: { marginTop: theme.spacing.md },
});
