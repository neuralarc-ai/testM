import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, Button } from 'react-native-paper';
import { theme } from '../theme/theme';

export default function DashboardScreen({ navigation }) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>Welcome to Manus AI</Title>
            <Text>Your autonomous AI assistant is ready to help!</Text>
            <Button 
              mode="contained" 
              onPress={() => navigation.navigate('CreateTask')}
              style={styles.button}
            >
              Create New Task
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
