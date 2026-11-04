<?php

namespace App\Http\Controllers;

use App\Models\ChatConversation;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ChatHistoryController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        return response()->json([
            'conversations' => $request->user()->chatConversations()->latest('updated_at')->get(['id', 'title', 'updated_at']),
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'conversation_id' => ['nullable', 'integer'],
            'messages' => ['required', 'array', 'max:50'],
            'messages.*.role' => ['required', 'in:user,assistant'],
            'messages.*.content' => ['required', 'string', 'max:5000'],
        ]);

        $conversation = $request->user()->chatConversations()->find($validated['conversation_id'] ?? null);
        $messages = $validated['messages'];

        if (! $conversation) {
            $conversation = $request->user()->chatConversations()->create([
                'title' => mb_substr($messages[0]['content'], 0, 120),
            ]);
        }

        $conversation->messages()->delete();
        $conversation->messages()->createMany($messages);
        $conversation->touch();

        return response()->json(['conversation_id' => $conversation->id]);
    }

    public function show(Request $request, ChatConversation $conversation): JsonResponse
    {
        abort_unless($conversation->user_id === $request->user()->id, 404);

        return response()->json([
            'conversation' => $conversation->load('messages:id,chat_conversation_id,role,content,created_at'),
        ]);
    }
}
